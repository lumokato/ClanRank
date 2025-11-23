const { createApp, ref, reactive, onMounted, watch, computed, nextTick } = Vue;

createApp({
    setup() {
        const state = reactive({
            is_current: true,
            is_history: false,
            loading: false,
            selectedServer: "1",
            selectedDate: "",
            selectedTime: "",
            selectedHistory: "",
            searchContents: "",
            TimeData: {},
            historyData: {},
            showData: [],
            pageinfo: {
                page: 0,
                maxPage: 0,
                limit: 10,
                prevDisabled: true,
                nextDisabled: true,
            },
            errorMsg: "",
            isDarkMode: false // Default to light mode
        });

        const apiUrl = "";

        const toggleTheme = () => {
            state.isDarkMode = !state.isDarkMode;
            updateTheme();
        };

        const updateTheme = () => {
            if (state.isDarkMode) {
                document.body.classList.add('dark-mode');
                localStorage.setItem('theme', 'dark');
            } else {
                document.body.classList.remove('dark-mode');
                localStorage.setItem('theme', 'light');
            }
        };

        // Load theme from local storage
        const loadTheme = () => {
            const savedTheme = localStorage.getItem('theme');
            if (savedTheme === 'dark') {
                state.isDarkMode = true;
                document.body.classList.add('dark-mode');
            } else {
                state.isDarkMode = false;
                document.body.classList.remove('dark-mode');
            }
        };

        const changeToCurrent = () => {
            state.is_current = true;
            state.is_history = false;
            loadTime();
        };

        const changeToHistory = () => {
            state.is_current = false;
            state.is_history = true;
            loadHistory();
        };

        const loadTime = async () => {
            state.loading = true;
            try {
                const res = await fetch(`${apiUrl}/current/getalltime/qd`);
                const data = await res.json();
                state.TimeData = data.data[state.selectedServer] || {};
                lastTime();
            } catch (e) {
                console.error(e);
                showError("无法加载时间数据");
            } finally {
                state.loading = false;
            }
        };

        const loadHistory = async () => {
            state.loading = true;
            try {
                const res = await fetch(`${apiUrl}/history/getalltime/qd`);
                const data = await res.json();
                state.historyData = data.data || {};
                lastHistoryTime();
            } catch (e) {
                console.error(e);
                showError("无法加载历史数据");
            } finally {
                state.loading = false;
            }
        };

        const lastTime = () => {
            const keys = Object.keys(state.TimeData);
            if (keys.length > 0) {
                const date = keys[keys.length - 1];
                state.selectedDate = date;
                const times = state.TimeData[date];
                state.selectedTime = times[times.length - 1];
            }
        };

        const lastHistoryTime = () => {
            const list = state.historyData[state.selectedServer];
            if (list && list.length > 0) {
                state.selectedHistory = list[list.length - 1];
            }
        };

        const searchDataFirstTime = () => {
            searchDataPage(0);
        };

        const searchDataPage = async (page) => {
            state.loading = true;
            state.pageinfo.page = page;

            let filename = "";
            if (state.is_current) {
                filename = `qd/${state.selectedServer}/${state.selectedDate}${state.selectedTime}`;
            } else {
                filename = `qd/history/${state.selectedServer}/${state.selectedHistory}`;
            }

            const payload = {
                filename: filename,
                search: state.searchContents,
                page: page,
                page_limit: state.pageinfo.limit
            };

            try {
                const res = await fetch(`${apiUrl}/search`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                processData(data);
            } catch (e) {
                console.error(e);
                showError("查询失败");
            } finally {
                state.loading = false;
            }
        };

        const searchScoreLine = async () => {
            state.loading = true;
            let filename = "";
            if (state.is_current) {
                filename = `qd/${state.selectedServer}/${state.selectedDate}${state.selectedTime}`;
            } else {
                filename = `qd/history/${state.selectedServer}/${state.selectedHistory}`;
            }
            const payload = {
                filename: filename,
                search: state.searchContents,
                page: 0,
                page_limit: state.pageinfo.limit
            };

            try {
                const res = await fetch(`${apiUrl}/search/scoreline`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                processData(data);
            } catch (e) {
                console.error(e);
                showError("查询失败");
            } finally {
                state.loading = false;
            }
        };

        const processData = (data) => {
            if (data.state !== 'success') {
                showError(data.error_message || "Unknown error");
                return;
            }
            state.showData = data.data;
            state.pageinfo.maxPage = Math.ceil(data.total / state.pageinfo.limit);
            state.pageinfo.prevDisabled = state.pageinfo.page === 0;
            state.pageinfo.nextDisabled = state.pageinfo.page >= state.pageinfo.maxPage - 1;
        };

        const addPage = (val) => {
            const newPage = state.pageinfo.page + val;
            if (newPage >= 0 && newPage < state.pageinfo.maxPage) {
                searchDataPage(newPage);
            }
        };

        const showError = (msg) => {
            state.errorOccured = true;
            state.errorMsg = msg;
            setTimeout(() => { state.errorOccured = false; }, 3000);
        };

        const parseDate = (str) => {
            if (!str) return "";
            return str.substr(0, 4) + '/' + str.substr(4, 2) + '/' + str.substr(6, 2);
        };

        const parseTime = (str) => {
            if (!str) return "";
            return str.substr(0, 2) + ':' + str.substr(2, 2);
        };

        onMounted(() => {
            loadTheme();
            loadTime();
        });

        watch(() => state.selectedDate, () => {
            if (state.TimeData && state.TimeData[state.selectedDate]) {
                const times = state.TimeData[state.selectedDate];
                state.selectedTime = times[times.length - 1];
            }
        });

        return {
            state,
            changeToCurrent,
            changeToHistory,
            searchDataFirstTime,
            searchScoreLine,
            addPage,
            parseDate,
            parseTime,
            toggleTheme
        };
    }
}).mount('#app');
