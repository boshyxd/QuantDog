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
    console.log('Raw honeypots from backend:', honeypots);
    console.log('Number of honeypots received:', honeypots.length);
    
    // Transform backend data to match frontend expectations
    const transformed = honeypots.map((hp: any, index: number) => {
      // Generate symbol based on blockchain type or default sequence
      let symbol = 'QTC'; // default
      if (hp.blockchain === 'ethereum') symbol = 'ETH';
      else if (hp.blockchain === 'bitcoin') symbol = 'BTC';
      else if (hp.blockchain === 'quantum') symbol = 'QTC';
      else {
        // For other cases, cycle through available symbols
        const symbols = ['ETH', 'BTC', 'QTC', 'SOL', 'ADA', 'DOT'];
        symbol = symbols[index % symbols.length];
      }

      // Generate mock address based on blockchain type
      let address = 'q1x4rt...8h9p'; // default quantum
      if (hp.blockchain === 'ethereum') {
        address = `0x${Math.random().toString(16).substr(2, 6)}...${Math.random().toString(16).substr(2, 4)}`;
      } else if (hp.blockchain === 'bitcoin') {
        address = `bc1q${Math.random().toString(16).substr(2, 6)}...${Math.random().toString(16).substr(2, 4)}`;
      } else {
        address = `q${Math.random().toString(16).substr(2, 6)}...${Math.random().toString(16).substr(2, 4)}`;
      }

      return {
        ...hp,
        symbol,
        address,
        balance: '0.0000',
        value: '$0.00',
        change: (Math.random() - 0.5) * 30, // Random change between -15 and +15
        starred: Math.random() > 0.7, // 30% chance of being starred
        threatLevel: hp.threat_indicators?.length > 0 ? 'high' : 
                     hp.status === 'triggered' ? 'medium' : 
                     hp.monitoring_sensitivity || 'low',
        protection: hp.protection_type || 'ecdsa',
        lastActivity: hp.last_interaction ? 
          new Date(hp.last_interaction).toLocaleString() : 
          `${Math.floor(Math.random() * 24) + 1} hours ago`
      };
    });
    
    console.log('Transformed honeypots for frontend:', transformed);
    console.log('Number of transformed honeypots:', transformed.length);
    return transformed;
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

  async enableHoneypot(honeypotId: string): Promise<void> {
    await this.fetchWithHandling(`/honeypots/${honeypotId}/enable`, {
      method: 'POST',
    });
  }

  async deleteHoneypot(honeypotId: string): Promise<void> {
    await this.fetchWithHandling(`/honeypots/${honeypotId}`, {
      method: 'DELETE',
    });
  }

  async deployHoneypot(config: {
    name: string
    blockchain: string
    protection_type: string
    monitoring_sensitivity: string
    auto_response: boolean
    description: string
  }): Promise<void> {
    await this.fetchWithHandling('/honeypots/deploy', {
      method: 'POST',
      body: JSON.stringify(config),
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