const WS_URL = 'ws://localhost:8000/ws';

export interface WebSocketMessage {
  type: string;
  data: any;
}

export interface HoneypotCompromisedData {
  honeypot_id: string;
  honeypot_name: string;
  wallet_address: string;
  amount_drained: number;
  blockchain: string;
  threat_level: string;
  auto_responded: boolean;
  timestamp: string;
  status: string;
}

export class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 3000;
  private listeners: Map<string, ((data: any) => void)[]> = new Map();

  connect(): void {
    try {
      this.ws = new WebSocket(WS_URL);

      this.ws.onopen = () => {
        console.log('🔗 WebSocket connected');
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          console.log('📨 WebSocket message received:', message);
          
          // Notify listeners for this message type
          const typeListeners = this.listeners.get(message.type) || [];
          typeListeners.forEach(listener => listener(message.data));
          
          // Also notify general listeners
          const generalListeners = this.listeners.get('*') || [];
          generalListeners.forEach(listener => listener(message));
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.ws.onclose = () => {
        console.log('🔌 WebSocket disconnected');
        this.ws = null;
        this.attemptReconnect();
      };

      this.ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
      };

    } catch (error) {
      console.error('Failed to connect to WebSocket:', error);
      this.attemptReconnect();
    }
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`🔄 Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
      
      setTimeout(() => {
        this.connect();
      }, this.reconnectDelay);
    } else {
      console.error('❌ Max reconnection attempts reached');
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  send(message: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected, cannot send message');
    }
  }

  // Subscribe to specific message types
  on(messageType: string, callback: (data: any) => void): () => void {
    if (!this.listeners.has(messageType)) {
      this.listeners.set(messageType, []);
    }
    
    const typeListeners = this.listeners.get(messageType)!;
    typeListeners.push(callback);

    // Return unsubscribe function
    return () => {
      const index = typeListeners.indexOf(callback);
      if (index > -1) {
        typeListeners.splice(index, 1);
      }
    };
  }

  // Subscribe to all messages
  onAny(callback: (message: WebSocketMessage) => void): () => void {
    return this.on('*', callback);
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  ping(): void {
    this.send('ping');
  }
}

// Create a singleton instance
export const webSocketService = new WebSocketService();