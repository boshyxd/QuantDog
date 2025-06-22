const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Types matching the backend models
export interface ThreatStatus {
  threat_level: number;
  status: 'low' | 'medium' | 'high' | 'critical';
  active_crypto: 'classical' | 'post_quantum';
  threshold: number;
  timestamp: string;
  message: string;
}

export interface Honeypot {
  id: string;
  name: string;
  status: string;
  last_interaction: string | null;
  interaction_count: number;
  threat_indicators: string[];
  // Additional frontend fields
  symbol?: string;
  address?: string;
  balance?: string;
  value?: string;
  change?: number;
  starred?: boolean;
  threatLevel?: 'low' | 'medium' | 'high';
  protection?: 'rsa' | 'ecdsa';
}

export interface HoneypotConfig {
  id: string;
  monitoring_sensitivity: 'low' | 'medium' | 'high';
  protection_type: 'rsa' | 'ecdsa';
  auto_response: boolean;
  routing_method: 'classical' | 'post_quantum';
}

export interface SystemSettings {
  email_alerts: boolean;
  push_notifications: boolean;
  threat_threshold: 'low' | 'medium' | 'high';
  auto_response: boolean;
  monitoring_interval: number;
  retention_period: number;
}

class ApiService {
  private async fetchWithHandling(url: string, options?: RequestInit) {
    try {
      const response = await fetch(`${API_BASE_URL}${url}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API call failed:', error);
      throw error;
    }
  }

  // Honeypot endpoints
  async getHoneypots(): Promise<Honeypot[]> {
    const honeypots = await this.fetchWithHandling('/honeypots');
    
    // Transform backend data to match frontend expectations
    return honeypots.map((hp: any, index: number) => ({
      ...hp,
      symbol: index === 0 ? 'ETH' : index === 1 ? 'BTC' : 'QTC',
      address: index === 0 ? '0x742d35...9e71' : index === 1 ? 'bc1qxy2k...gdjq' : 'q1x4rt...8h9p',
      balance: '0.0000',
      value: '$0.00',
      change: index === 1 ? 15.2 : index === 2 ? -5.1 : 0,
      starred: index === 1,
      threatLevel: hp.threat_indicators.length > 0 ? 'high' : 
                   hp.status === 'triggered' ? 'medium' : 'low',
      protection: index % 2 === 0 ? 'ecdsa' : 'rsa',
      lastActivity: hp.last_interaction ? 
        new Date(hp.last_interaction).toLocaleString() : 
        `${Math.floor(Math.random() * 24) + 1} hours ago`
    }));
  }

  async getHoneypotConfig(honeypotId: string): Promise<HoneypotConfig> {
    // This endpoint would need to be added to the backend
    // For now, return mock config
    return {
      id: honeypotId,
      monitoring_sensitivity: 'medium',
      protection_type: 'ecdsa',
      auto_response: true,
      routing_method: 'classical'
    };
  }

  async updateHoneypotConfig(honeypotId: string, config: Partial<HoneypotConfig>): Promise<void> {
    await this.fetchWithHandling(`/honeypots/${honeypotId}/config`, {
      method: 'PUT',
      body: JSON.stringify(config),
    });
  }

  async disableHoneypot(honeypotId: string): Promise<void> {
    await this.fetchWithHandling(`/honeypots/${honeypotId}/disable`, {
      method: 'POST',
    });
  }

  // System settings endpoints
  async getSystemSettings(): Promise<SystemSettings> {
    // This endpoint would need to be added to the backend
    // For now, return mock settings
    return {
      email_alerts: true,
      push_notifications: false,
      threat_threshold: 'medium',
      auto_response: true,
      monitoring_interval: 5,
      retention_period: 30
    };
  }

  async updateSystemSettings(settings: Partial<SystemSettings>): Promise<void> {
    await this.fetchWithHandling('/settings', {
      method: 'PUT',
      body: JSON.stringify(settings),
    });
  }

  // Status endpoints
  async getStatus(): Promise<ThreatStatus> {
    return await this.fetchWithHandling('/status');
  }

  async simulateAttack(intensity: number = 50, duration?: number): Promise<ThreatStatus> {
    return await this.fetchWithHandling('/simulate/attack', {
      method: 'POST',
      body: JSON.stringify({ intensity, duration }),
    });
  }

  async reduceThreat(amount: number = 10): Promise<ThreatStatus> {
    return await this.fetchWithHandling('/simulate/reduce-threat', {
      method: 'POST',
      body: JSON.stringify({ amount }),
    });
  }

  // Crypto method endpoints
  async switchCryptoMethod(method: 'classical' | 'post_quantum'): Promise<void> {
    await this.fetchWithHandling(`/crypto/switch/${method}`, {
      method: 'POST',
    });
  }
}

export const apiService = new ApiService();