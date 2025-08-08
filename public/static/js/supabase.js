// MYSC IR Platform - Supabase 실시간 연동
class SupabaseRealtime {
    constructor() {
        // Production Supabase Environment
        this.supabaseUrl = 'https://isoufdbcdcwgnqldyxpk.supabase.co';
        this.supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlzb3VmZGJjZGN3Z25xbGR5eHBrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ2MjgzODMsImV4cCI6MjA3MDIwNDM4M30.t76CmPYWyQ6wh0wgKoPdFMUnU7IdJ47T-7ES7ShpVog';
        this.socket = null;
        this.subscriptions = new Map();
    }

    // 실시간 연결 초기화
    async initializeConnection() {
        if (!this.supabaseUrl || !this.supabaseAnonKey) {
            console.warn('Supabase credentials not configured');
            return;
        }

        try {
            // WebSocket 연결 설정
            const wsUrl = this.supabaseUrl.replace('https:', 'wss:').replace('http:', 'ws:') + '/realtime/v1/websocket';
            this.socket = new WebSocket(wsUrl + `?apikey=${this.supabaseAnonKey}`);
            
            this.socket.onopen = () => {
                console.log('✅ Supabase Realtime connected');
                this.sendHeartbeat();
            };
            
            this.socket.onmessage = (event) => {
                this.handleMessage(JSON.parse(event.data));
            };
            
            this.socket.onclose = () => {
                console.log('❌ Supabase Realtime disconnected');
                // 자동 재연결
                setTimeout(() => this.initializeConnection(), 5000);
            };
            
            this.socket.onerror = (error) => {
                console.error('Supabase Realtime error:', error);
            };
            
        } catch (error) {
            console.error('Failed to initialize Supabase connection:', error);
        }
    }

    // 대화 메시지 실시간 구독
    subscribeToConversation(sessionId, callback) {
        if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
            console.warn('WebSocket not ready, queuing subscription');
            setTimeout(() => this.subscribeToConversation(sessionId, callback), 1000);
            return;
        }

        const subscriptionId = `conversation_${sessionId}`;
        
        // 이미 구독 중인 경우 제거
        if (this.subscriptions.has(subscriptionId)) {
            this.unsubscribe(subscriptionId);
        }

        const subscription = {
            event: 'INSERT',
            schema: 'public',
            table: 'conversation_messages',
            filter: `session_id=eq.${sessionId}`,
            callback: callback
        };

        this.subscriptions.set(subscriptionId, subscription);
        
        // 구독 메시지 전송
        this.socket.send(JSON.stringify({
            topic: `realtime:public:conversation_messages:session_id=eq.${sessionId}`,
            event: 'phx_join',
            payload: {},
            ref: subscriptionId
        }));

        return subscriptionId;
    }

    // 분석 결과 실시간 구독
    subscribeToAnalysisResults(projectId, callback) {
        if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
            setTimeout(() => this.subscribeToAnalysisResults(projectId, callback), 1000);
            return;
        }

        const subscriptionId = `analysis_${projectId}`;
        
        if (this.subscriptions.has(subscriptionId)) {
            this.unsubscribe(subscriptionId);
        }

        const subscription = {
            event: 'INSERT',
            schema: 'public', 
            table: 'analysis_results',
            filter: `project_id=eq.${projectId}`,
            callback: callback
        };

        this.subscriptions.set(subscriptionId, subscription);
        
        this.socket.send(JSON.stringify({
            topic: `realtime:public:analysis_results:project_id=eq.${projectId}`,
            event: 'phx_join',
            payload: {},
            ref: subscriptionId
        }));

        return subscriptionId;
    }

    // 구독 해제
    unsubscribe(subscriptionId) {
        if (this.subscriptions.has(subscriptionId)) {
            this.socket?.send(JSON.stringify({
                topic: `realtime:${subscriptionId}`,
                event: 'phx_leave',
                payload: {},
                ref: subscriptionId
            }));
            this.subscriptions.delete(subscriptionId);
        }
    }

    // 메시지 처리
    handleMessage(message) {
        if (message.event === 'postgres_changes') {
            const payload = message.payload;
            const table = payload.table;
            const eventType = payload.eventType;
            const record = payload.new || payload.old;

            // 구독별로 콜백 실행
            for (const [subscriptionId, subscription] of this.subscriptions) {
                if (subscription.table === table && subscription.event === eventType) {
                    // 필터 검사
                    if (this.matchesFilter(record, subscription.filter)) {
                        subscription.callback(record, eventType);
                    }
                }
            }
        }
    }

    // 필터 매칭 검사
    matchesFilter(record, filter) {
        if (!filter) return true;
        
        // 간단한 필터 파싱 (예: "session_id=eq.uuid")
        const [field, operator, value] = filter.split(/[=\.]/);
        if (operator === 'eq') {
            return record[field] === value;
        }
        
        return true;
    }

    // 하트비트 전송 (연결 유지)
    sendHeartbeat() {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                topic: 'phoenix',
                event: 'heartbeat',
                payload: {},
                ref: Date.now()
            }));
        }
        
        // 30초마다 하트비트
        setTimeout(() => this.sendHeartbeat(), 30000);
    }

    // HTTP API 헬퍼 메서드들
    async fetchConversationHistory(sessionId) {
        try {
            const response = await fetch(`${this.supabaseUrl}/rest/v1/conversation_messages?session_id=eq.${sessionId}&select=*&order=created_at`, {
                headers: {
                    'Authorization': `Bearer ${this.supabaseAnonKey}`,
                    'apikey': this.supabaseAnonKey
                }
            });
            return await response.json();
        } catch (error) {
            console.error('Failed to fetch conversation history:', error);
            return [];
        }
    }

    async fetchAnalysisResults(projectId) {
        try {
            const response = await fetch(`${this.supabaseUrl}/rest/v1/analysis_results?project_id=eq.${projectId}&select=*&order=created_at`, {
                headers: {
                    'Authorization': `Bearer ${this.supabaseAnonKey}`,
                    'apikey': this.supabaseAnonKey
                }
            });
            return await response.json();
        } catch (error) {
            console.error('Failed to fetch analysis results:', error);
            return [];
        }
    }

    // 연결 종료
    disconnect() {
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
        this.subscriptions.clear();
    }
}

// 전역 인스턴스 생성
window.supabaseRealtime = new SupabaseRealtime();