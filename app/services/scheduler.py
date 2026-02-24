from apscheduler.schedulers.background import BackgroundScheduler
import logging
import datetime
import os
import shutil
import calendar
import json
from . import farm_service
from . import clanbattle_service
from . import bilievent_service

logger = logging.getLogger(__name__)

CONFIG_PATH = os.path.join('config', 'config.json')

def load_config():
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        logger.error(f"加载配置文件失败: {e}")
        return None

def move_data():
    # 尝试加载配置，如果存在配置则使用配置中的年月，否则使用当前时间
    config = load_config()
    
    if config:
        year = int(config.get('year', datetime.datetime.now().year))
        month = int(config.get('month', datetime.datetime.now().month))
    else:
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
    
    dt = datetime.date(year, month, 15) # 选月中某天防止跨月计算问题
    prev_month_date = dt - datetime.timedelta(days=30)
    
    target_year = str(prev_month_date.year)
    target_month = str(prev_month_date.month).zfill(2)
    
    dir_path = os.getcwd()
    source_dir = os.path.join(dir_path, 'qd', '1')
    history_dir = os.path.join(dir_path, 'qd', 'history', '1')
    history_backup_dir = os.path.join(dir_path, 'qd', 'history', f"{target_year[2:]}-{target_month}")

    if not os.path.exists(history_dir):
        os.makedirs(history_dir)
        
    if not os.path.exists(source_dir):
        logger.warning(f"源目录 {source_dir} 不存在。")
        return

    files = os.listdir(source_dir)
    if not files:
        logger.info("qd/1 中没有文件需要移动。")
        return

    files.sort(key=lambda x: int(x[:-4]) if x[:-4].isdigit() else 0)
    last_file = files[-1]
    
    target_file = os.path.join(history_dir, f"{target_year}年{target_month}月.csv")
    
    try:
        # 1. 将最后一个文件复制到 history/1/YYYY年MM月.csv
        shutil.copyfile(os.path.join(source_dir, last_file), target_file)
        logger.info(f"已复制 {last_file} 到 {target_file}")
        
        # 2. 将整个文件夹移动到 history/YY-MM
        # 如果目标存在，先删除（防止数据丢失的保险在下面：先copytree再rmtree）
        if os.path.exists(history_backup_dir):
            # 为了保险，可以重命名旧的备份而不是直接删除，或者假设本次是更新
            shutil.rmtree(history_backup_dir) 
        
        # 先复制以确保成功，然后再删除源文件
        shutil.copytree(source_dir, history_backup_dir, dirs_exist_ok=True)
        logger.info(f"已备份 {source_dir} 到 {history_backup_dir}")
        
        # 3. 清理源目录
        # 验证复制是否成功
        if os.path.exists(target_file) and os.path.exists(history_backup_dir):
            shutil.rmtree(source_dir)
            os.makedirs(source_dir)
            logger.info("源目录已清理并重建。")
        else:
            logger.error("验证失败，未删除源文件。")
            
    except Exception as e:
        logger.error(f"移动数据时出错: {e}")


def user_remove(clear_type):
    total = farm_service.get_account_data()
    farm_service.user_clear(0, total["passwd"], clear_type)

def init_scheduler(scheduler):
    # 默认逻辑：每月倒数第6天到倒数第2天（共5天）
    today = datetime.datetime.today()
    monthdays = calendar.monthrange(today.year, today.month)[1]
    
    # 默认开始时间：倒数第6天 05:00
    default_start_day = monthdays - 5
    
    year = today.year
    month = today.month
    start_day = default_start_day
    
    # 检查是否有配置文件覆盖默认逻辑
    config = load_config()
    use_config = False
    
    if config:
        config_year = config.get('year', year)
        config_month = config.get('month', month)
        
        # 如果配置的月份是当前月份，则采用配置
        if config_year == year and config_month == month:
            logger.info("检测到当前月份的配置文件，使用配置参数。")
            start_day = config.get('start_day', start_day)
            use_config = True
        else:
            logger.info("配置文件并非当前月份，忽略配置，使用默认逻辑。")
    else:
        logger.info("未检测到配置文件，使用默认会战时间逻辑。")
    
    # 固定为5天：从 start_day 开始，到 start_day + 4 结束
    # 例如：24号开始，24, 25, 26, 27, 28，结束日期为28号
    end_day = start_day + 4
    
    start_time = datetime.datetime(year, month, start_day, 5, 30)
    # 结束时间设为结束日期的 23:59:59
    end_time = datetime.datetime(year, month, end_day, 23, 59, 59)

    # 暂时禁用 Bilibili 活动接口
    # if bilievent_service.time_battle_bilibili(datetime.datetime.now()):
    #     start_time, end_time = bilievent_service.time_battle_bilibili(datetime.datetime.now())
    
    # 安全地调度数据迁移
    # 在会战开始前一天运行
    move_date = start_time - datetime.timedelta(days=1)
    scheduler.add_job(move_data, 'date', run_date=move_date)
    
    # 阶段数据收集
    scheduler.add_job(clanbattle_service.stage_data, 'interval', minutes=30, start_date=start_time+datetime.timedelta(minutes=2), end_date=end_time)
    
    # 最后一次阶段数据收集：会战结束约10天后的15点
    final_check_time = end_time + datetime.timedelta(days=10)
    final_check_time = final_check_time.replace(hour=15, minute=0, second=0, microsecond=0)
    scheduler.add_job(clanbattle_service.stage_data, 'date', run_date=final_check_time, args=[1])

