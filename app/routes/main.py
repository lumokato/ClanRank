from flask import Blueprint, render_template, jsonify, request
import os
import pandas as pd
import json

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

def get_time_data(base_path):
    data = {}
    if not os.path.exists(base_path):
        return data
    
    # Structure: server -> date -> [times]
    # qd/1/202310271200.csv
    # qd/history/1/202310.csv (History is different structure?)
    
    # Let's look at the file structure from list_dir earlier.
    # qd/1 seems to contain CSVs.
    # qd/history/1 seems to contain CSVs.
    
    # For current: qd/{server}/{filename}.csv
    # Filename format: YYYYMMDDHHMM.csv?
    # Let's assume standard format based on bilicompare.py: 
    # filename = str(end_time.strftime("%Y%m%d%H")) + str(int(int(end_time.strftime("%M"))/30)*30).zfill(2)
    # So YYYYMMDDHHMM
    
    # User clarified there is only one server (Server 1)
    servers = ['1'] 
    for server in servers:
        server_path = os.path.join(base_path, server)
        if not os.path.exists(server_path):
            continue
        
        data[server] = {}
        files = os.listdir(server_path)
        files.sort()
        
        for f in files:
            if not f.endswith('.csv'):
                continue
            # 202310271200.csv
            if len(f) < 12: 
                continue
            date = f[:8]
            time = f[8:12]
            if date not in data[server]:
                data[server][date] = []
            data[server][date].append(time)
            
    return data

def get_history_data(base_path):
    data = {}
    if not os.path.exists(base_path):
        return data
        
    servers = ['1']
    for server in servers:
        server_path = os.path.join(base_path, server)
        if not os.path.exists(server_path):
            continue
            
        files = os.listdir(server_path)
        files.sort()
        data[server] = [f.replace('.csv', '') for f in files if f.endswith('.csv')]
        
    return data

@main_bp.route('/current/getalltime/qd')
def get_current_time():
    # Assuming 'qd' is in root
    data = get_time_data('qd')
    return jsonify({'state': 'success', 'data': data})

@main_bp.route('/history/getalltime/qd')
def get_history_time():
    data = get_history_data('qd/history')
    return jsonify({'state': 'success', 'data': data})

@main_bp.route('/search', methods=['POST'])
def search():
    req = request.json
    filename = req.get('filename')
    search_term = req.get('search', '')
    page = req.get('page', 0)
    limit = req.get('page_limit', 10)
    # Default to Clan Name (2) if type is not provided or if we removed the selector
    search_type = req.get('type', '2') 
    
    if not filename.endswith('.csv'):
        filename += '.csv'
        
    if not os.path.exists(filename):
        return jsonify({'state': 'fail', 'error_message': 'File not found'})
        
    try:
        df = pd.read_csv(filename)
        # Filter
        if search_term:
            if search_type == '1': # Rank
                df = df[df['rank'].astype(str) == search_term]
            elif search_type == '2': # Clan Name
                df = df[df['clan_name'].astype(str).str.contains(search_term, na=False)]
            elif search_type == '3': # Leader Name
                df = df[df['leader_name'].astype(str).str.contains(search_term, na=False)]
        
        total = len(df)
        start = page * limit
        end = start + limit
        
        result = df.iloc[start:end].to_dict('records')
        
        return jsonify({'state': 'success', 'data': result, 'total': total, 'page': page})
    except Exception as e:
        return jsonify({'state': 'fail', 'error_message': str(e)})

@main_bp.route('/search/scoreline', methods=['POST'])
def search_scoreline():
    req = request.json
    filename = req.get('filename')
    search_term = req.get('search', '')
    
    if not filename.endswith('.csv'):
        filename += '.csv'
        
    if not os.path.exists(filename):
        return jsonify({'state': 'fail', 'error_message': 'File not found'})
        
    try:
        df = pd.read_csv(filename)
        result_df = pd.DataFrame()
        
        if search_term and search_term.isdigit():
            # Search for specific rank
            result_df = df[df['rank'] == int(search_term)]
        else:
            # Standard cutoffs
            cutoffs = [2, 10, 30, 50, 100, 200, 400, 800, 1500, 2500]
            result_df = df[df['rank'].isin(cutoffs)]
            
        result = result_df.to_dict('records')
        return jsonify({'state': 'success', 'data': result, 'total': len(result), 'page': 0})
    except Exception as e:
        return jsonify({'state': 'fail', 'error_message': str(e)})
