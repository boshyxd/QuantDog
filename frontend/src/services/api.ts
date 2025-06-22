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
  starred: boolean;
  activated_at: string | null;
  wallet_address: string | null;
  current_balance: number | null;
  initial_balance: number | null;
  blockchain?: string;
  protection_type?: string;
  monitoring_sensitivity?: string;
  description?: string;
  // Additional frontend fields
  symbol?: string;
  address?: string;
  balance?: string;
  value?: string;
  change?: number;
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
      // Generate symbol based on blockchain type
      let symbol = 'QTC'; // default
      if (hp.blockchain === 'ethereum') symbol = 'ETH';
      else if (hp.blockchain === 'bitcoin') symbol = 'BTC';
      else if (hp.blockchain === 'quantum') symbol = 'QTC';

      // Format wallet address for display (shorten it)
      let address = hp.wallet_address || '';
      if (address.length > 10) {
        address = `${address.substring(0, 6)}...${address.substring(address.length - 4)}`;
      }

      // Calculate time since activation
      let lastActivity = 'Never';
      if (hp.last_interaction) {
        lastActivity = new Date(hp.last_interaction).toLocaleString();
      } else if (hp.activated_at) {
        const activatedDate = new Date(hp.activated_at);
        const now = new Date();
        const diffMs = now.getTime() - activatedDate.getTime();
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        const diffMins = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
        
        if (diffHours > 0) {
          lastActivity = `Active for ${diffHours}h ${diffMins}m`;
        } else {
          lastActivity = `Active for ${diffMins}m`;
        }
      }

      // Format balance and value
      const balance = hp.current_balance !== null ? hp.current_balance.toFixed(4) : '0.0000';
      let value = '$0.00';
      if (hp.current_balance !== null) {
        // Mock price calculation based on blockchain
        const prices: Record<string, number> = {
          'ethereum': 2000,
          'bitcoin': 45000,
          'quantum': 10
        };
        const price = prices[hp.blockchain || 'quantum'] || 10;
        value = `$${(hp.current_balance * price).toFixed(2)}`;
      }

      // Calculate change based on balance difference
      let change = 0;
      if (hp.initial_balance && hp.current_balance !== null) {
        change = ((hp.current_balance - hp.initial_balance) / hp.initial_balance) * 100;
      }

      return {
        ...hp,
        symbol,
        address,
        balance,
        value,
        change,
        threatLevel: hp.threat_indicators?.length > 0 ? 'high' : 
                     hp.status === 'triggered' ? 'high' : 
                     hp.monitoring_sensitivity || 'low',
        protection: hp.protection_type || 'ecdsa',
        lastActivity
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

  async toggleHoneypotStar(honeypotId: string): Promise<{ starred: boolean }> {
    const result = await this.fetchWithHandling(`/honeypots/${honeypotId}/star`, {
      method: 'POST',
    });
    return result;
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