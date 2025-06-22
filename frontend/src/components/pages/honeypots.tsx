import * as React from "react"
import { motion, AnimatePresence, useInView } from "motion/react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from "@/components/ui/dropdown-menu"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Switch } from "@/components/ui/switch"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { HoverCard, HoverCardContent, HoverCardTrigger } from "@/components/ui/hover-card"
import { Separator } from "@/components/ui/separator"
import { GiHoneypot } from "react-icons/gi"
import { 
  SiHackerone,
  SiCyberdefenders,
  SiFirebase,
  SiBitcoin,
  SiEthereum
} from "react-icons/si"
import { 
  MdSecurity,
  MdNetworkCheck,
  MdRadar,
  MdBugReport,
  MdMonitorHeart
} from "react-icons/md"
import { 
  FaShieldAlt,
  FaNetworkWired,
  FaEye,
  FaRobot,
  FaBrain,
  FaCode,
  FaServer
} from "react-icons/fa"
import { 
  HiShieldCheck,
  HiCpuChip,
  HiFingerPrint
} from "react-icons/hi2"
import { 
  MoreHorizontal,
  TrendingUp,
  TrendingDown,
  ArrowUpRight,
  Star,
  Eye,
  Activity,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Settings,
  Download,
  Share,
  BarChart3,
  Zap,
  Lock,
  Globe,
  Cpu,
  Wifi,
  RefreshCw,
  Trash2
} from "lucide-react"
import { apiService, type Honeypot } from "@/services/api"
import { webSocketService, type HoneypotCompromisedData } from "@/services/websocket"
import { toast } from "sonner"

// Honeypots data will be fetched from API

const getStatusBadge = (status: string) => {
  switch (status) {
    case "active":
      return <Badge variant="secondary" className="bg-green-500/10 text-green-400 border-green-500/20"><CheckCircle className="w-3 h-3 mr-1" />Active</Badge>
    case "triggered":
      return <Badge variant="destructive" className="bg-red-500/10 text-red-400 border-red-500/20"><AlertTriangle className="w-3 h-3 mr-1" />Triggered</Badge>
    case "monitoring":
      return <Badge variant="outline" className="bg-blue-500/10 text-blue-400 border-blue-500/20"><Eye className="w-3 h-3 mr-1" />Monitoring</Badge>
    case "disabled":
      return <Badge variant="outline" className="bg-gray-500/10 text-muted-foreground border-gray-500/20"><XCircle className="w-3 h-3 mr-1" />Disabled</Badge>
    default:
      return <Badge variant="outline"><XCircle className="w-3 h-3 mr-1" />Unknown</Badge>
  }
}

const getThreatLevelColor = (level: string) => {
  switch (level) {
    case "low": return "text-green-400"
    case "medium": return "text-yellow-400"
    case "high": return "text-red-400"
    default: return "text-muted-foreground"
  }
}

const getThreatProgress = (level: string) => {
  switch (level) {
    case "low": return 25
    case "medium": return 60
    case "high": return 85
    default: return 0
  }
}

export function HoneypotsPage() {
  const ref = React.useRef(null)
  const isInView = useInView(ref, { once: true })
  
  // Dialog state management
  const [alertsDialogOpen, setAlertsDialogOpen] = React.useState(false)
  const [notificationDialogOpen, setNotificationDialogOpen] = React.useState(false)
  const [advancedDialogOpen, setAdvancedDialogOpen] = React.useState(false)
  const [honeypotDialogOpen, setHoneypotDialogOpen] = React.useState<string | null>(null)
  const [deployDialogOpen, setDeployDialogOpen] = React.useState(false)
  
  // Data state
  const [honeypots, setHoneypots] = React.useState<Honeypot[]>([])
  
  // Form state for honeypot configuration
  const [configForm, setConfigForm] = React.useState<{[key: string]: {
    monitoring_sensitivity: string
    protection_type: string
    auto_response: boolean
  }}>({})
  
  // Initialize form state when honeypots change
  React.useEffect(() => {
    const initialConfig: {[key: string]: {
      monitoring_sensitivity: string
      protection_type: string
      auto_response: boolean
    }} = {}
    
    honeypots.forEach(honeypot => {
      initialConfig[honeypot.id] = {
        monitoring_sensitivity: honeypot.threatLevel || 'medium',
        protection_type: honeypot.protection || 'ecdsa',
        auto_response: true
      }
    })
    
    setConfigForm(initialConfig)
  }, [honeypots])
  
  // Deploy form state
  const [deployForm, setDeployForm] = React.useState({
    name: '',
    blockchain: 'ethereum',
    protection_type: 'ecdsa',
    monitoring_sensitivity: 'medium',
    auto_response: true,
    description: ''
  })
  
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState<string | null>(null)
  
  // Settings state
  const [settings, setSettings] = React.useState({
    emailAlerts: true,
    pushNotifications: false,
    threatThreshold: "medium",
    autoResponse: true,
    monitoringInterval: "5",
    retentionPeriod: "30"
  })
  
  // Fetch honeypots data
  const fetchHoneypots = React.useCallback(async () => {
    try {
      setLoading(true)
      const data = await apiService.getHoneypots()
      setHoneypots(data)
      setError(null)
    } catch (err) {
      setError('Failed to load honeypots')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }, [])
  
  // Initial load and WebSocket setup
  React.useEffect(() => {
    fetchHoneypots()
    
    // Connect to WebSocket for real-time updates
    webSocketService.connect()
    
    // Listen for honeypot compromised events
    const unsubscribeCompromised = webSocketService.on('honeypot_compromised', (data: HoneypotCompromisedData) => {
      console.log('🚨 Honeypot compromised event received:', data)
      
      // Show toast notification with critical styling
      toast.error(`CRITICAL: ${data.honeypot_name} COMPROMISED!`, {
        description: `${data.amount_drained} ${data.blockchain.toUpperCase()} drained from ${data.wallet_address}. Auto-response: ${data.auto_responded ? 'Active' : 'Inactive'}`,
        duration: 10000, // Show for 10 seconds
        action: {
          label: "View Details",
          onClick: () => console.log("Viewing honeypot details")
        }
      })
      
      // Refresh honeypots data
      fetchHoneypots()
    })
    
    // Listen for general honeypot updates
    const unsubscribeUpdates = webSocketService.on('honeypots_updated', () => {
      console.log('🔄 Honeypots updated event received, refreshing data...')
      fetchHoneypots()
    })
    
    // Cleanup on unmount
    return () => {
      unsubscribeCompromised()
      unsubscribeUpdates()
      webSocketService.disconnect()
    }
  }, [])
  
  // Handle honeypot configuration
  const handleConfigureHoneypot = async (honeypotId: string, config: any) => {
    try {
      await apiService.updateHoneypotConfig(honeypotId, config)
      // Refresh data
      await fetchHoneypots()
      setHoneypotDialogOpen(null)
    } catch (err) {
      console.error('Failed to update honeypot config:', err)
    }
  }
  
  // Handle honeypot disable
  const handleDisableHoneypot = async (honeypotId: string) => {
    try {
      await apiService.disableHoneypot(honeypotId)
      // Refresh data
      await fetchHoneypots()
      setHoneypotDialogOpen(null)
    } catch (err) {
      console.error('Failed to disable honeypot:', err)
    }
  }

  // Handle honeypot enable
  const handleEnableHoneypot = async (honeypotId: string) => {
    try {
      await apiService.enableHoneypot(honeypotId)
      // Refresh data
      await fetchHoneypots()
      setHoneypotDialogOpen(null)
    } catch (err) {
      console.error('Failed to enable honeypot:', err)
    }
  }

  // Handle honeypot delete
  const handleDeleteHoneypot = async (honeypotId: string) => {
    try {
      await apiService.deleteHoneypot(honeypotId)
      // Refresh data
      await fetchHoneypots()
      setHoneypotDialogOpen(null)
    } catch (err) {
      console.error('Failed to delete honeypot:', err)
    }
  }

  // Handle star toggle
  const handleStarToggle = async (honeypotId: string) => {
    try {
      const result = await apiService.toggleHoneypotStar(honeypotId)
      // Update local state immediately for better UX
      setHoneypots(prev => prev.map(hp => 
        hp.id === honeypotId ? { ...hp, starred: result.starred } : hp
      ))
    } catch (err) {
      console.error('Failed to toggle star:', err)
      // Refresh to get correct state
      await fetchHoneypots()
    }
  }
  
  // Handle deploy new honeypot
  const handleDeployHoneypot = async () => {
    try {
      await apiService.deployHoneypot(deployForm)
      // Refresh data
      await fetchHoneypots()
      // Reset form
      setDeployForm({
        name: '',
        blockchain: 'ethereum',
        protection_type: 'ecdsa',
        monitoring_sensitivity: 'medium',
        auto_response: true,
        description: ''
      })
      setDeployDialogOpen(false)
    } catch (err) {
      console.error('Failed to deploy honeypot:', err)
    }
  }
  
  // Handle settings update
  const handleUpdateSettings = async () => {
    try {
      await apiService.updateSystemSettings({
        email_alerts: settings.emailAlerts,
        push_notifications: settings.pushNotifications,
        threat_threshold: settings.threatThreshold,
        auto_response: settings.autoResponse,
        monitoring_interval: parseInt(settings.monitoringInterval),
        retention_period: parseInt(settings.retentionPeriod)
      })
      // Close dialogs
      setAlertsDialogOpen(false)
      setNotificationDialogOpen(false)
      setAdvancedDialogOpen(false)
    } catch (err) {
      console.error('Failed to update settings:', err)
    }
  }

  return (
    <TooltipProvider>
      <motion.div 
        ref={ref}
        className="flex-1 bg-background text-foreground"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        <div className="p-6">
          {/* Header with Actions */}
          <motion.div 
            className="flex items-center justify-between mb-6"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            <div>
              <motion.h1 
                className="text-2xl font-bold mb-2"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
              >
                Honeypot Dashboard
              </motion.h1>
              <motion.p 
                className="text-muted-foreground"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.3 }}
              >
                Monitor and manage your quantum-protected honeypots
              </motion.p>
            </div>
            <motion.div 
              className="flex items-center gap-2"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="border-border bg-transparent text-foreground hover:bg-accent hover:text-foreground"
                    onClick={fetchHoneypots}
                    disabled={loading}
                  >
                    <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                    Refresh
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Refresh honeypot data</p>
                </TooltipContent>
              </Tooltip>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="outline" size="sm" className="border-border bg-transparent text-foreground hover:bg-accent hover:text-foreground">
                    <Download className="w-4 h-4 mr-2" />Export
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Export honeypot data</p>
                </TooltipContent>
              </Tooltip>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="sm" className="border-border bg-transparent text-foreground hover:bg-accent hover:text-foreground">
                    <Settings className="w-4 h-4 mr-2" />Settings
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="bg-card border-border">
                  <DropdownMenuItem 
                    className="text-foreground hover:bg-accent focus:bg-accent focus:text-foreground cursor-pointer"
                    onClick={() => setAlertsDialogOpen(true)}
                  >
                    Configure Alerts
                  </DropdownMenuItem>
                  <DropdownMenuItem 
                    className="text-foreground hover:bg-accent focus:bg-accent focus:text-foreground cursor-pointer"
                    onClick={() => setNotificationDialogOpen(true)}
                  >
                    Notification Settings
                  </DropdownMenuItem>
                  <DropdownMenuSeparator className="bg-secondary" />
                  <DropdownMenuItem 
                    className="text-foreground hover:bg-accent focus:bg-accent focus:text-foreground cursor-pointer"
                    onClick={() => setAdvancedDialogOpen(true)}
                  >
                    Advanced Settings
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </motion.div>
          </motion.div>

          {/* Alert */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.5 }}
          >
            <Alert className="mb-6 bg-green-500/10 border-green-500/20">
              <HiShieldCheck className="h-4 w-4 text-green-400" />
              <AlertDescription className="text-green-200">
                <strong>System Protection Active:</strong> All honeypots are using standard cryptography (RSA/ECDSA). Post-quantum routing activates when threats are detected.
              </AlertDescription>
            </Alert>
          </motion.div>

          {/* Portfolio Value */}
          <motion.div 
            className="mb-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.6 }}
          >
            <p className="text-muted-foreground text-sm mb-1">Total Portfolio Value</p>
            <motion.h2 
              className="text-3xl font-semibold"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.6, delay: 0.7 }}
            >
              $0.00
            </motion.h2>
            <div className="flex items-center gap-2 mt-2">
              <span className="text-muted-foreground text-sm">24h</span>
              <span className="text-green-500 text-sm flex items-center">
                <TrendingUp className="w-3 h-3 mr-1" />
                0.00%
              </span>
            </div>
          </motion.div>

          {/* Quick Stats */}
          <motion.div 
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.8 }}
          >
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.9 }}
            >
              <Card className="bg-card border-border hover:bg-accent/50 transition-colors h-32">
                <CardContent className="p-4 h-full flex items-center">
                  <div className="flex items-center justify-between w-full">
                    <div>
                      <p className="text-muted-foreground text-sm">Active Honeypots</p>
                      <p className="text-xl font-semibold mt-1 text-foreground">{honeypots.length}</p>
                    </div>
                    <motion.div
                      animate={{ rotate: [0, 10, 0] }}
                      transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                    >
                      <GiHoneypot className="w-8 h-8 text-amber-400" />
                    </motion.div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 1.0 }}
            >
              <Card className="bg-card border-border hover:bg-accent/50 transition-colors h-32">
                <CardContent className="p-4 h-full flex flex-col justify-between">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-muted-foreground text-sm">Total Interactions</p>
                      <p className="text-xl font-semibold mt-1 text-foreground">
                        {honeypots.reduce((acc, hp) => acc + hp.interaction_count, 0)}
                      </p>
                    </div>
                    <motion.div
                      animate={{ scale: [1, 1.1, 1] }}
                      transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                    >
                      <MdNetworkCheck className="w-8 h-8 text-blue-400" />
                    </motion.div>
                  </div>
                  <div className="flex items-center text-sm">
                    <TrendingUp className="w-3 h-3 text-green-400 mr-1" />
                    <span className="text-green-400">+23% from last week</span>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 1.1 }}
            >
              <Card className="bg-card border-border hover:bg-accent/50 transition-colors h-32">
                <CardContent className="p-4 h-full flex items-center">
                  <div className="flex items-center justify-between w-full">
                    <div>
                      <p className="text-muted-foreground text-sm">Threat Detection</p>
                      <p className="text-xl font-semibold mt-1 text-foreground">98.7%</p>
                    </div>
                    <motion.div
                      animate={{ rotate: [0, 360] }}
                      transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
                    >
                      <MdRadar className="w-8 h-8 text-yellow-400" />
                    </motion.div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 1.2 }}
            >
              <Card className="bg-card border-border hover:bg-accent/50 transition-colors h-32">
                <CardContent className="p-4 h-full flex flex-col justify-between">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-muted-foreground text-sm">Security Score</p>
                      <p className="text-xl font-semibold mt-1 text-green-400">Excellent</p>
                    </div>
                    <motion.div
                      animate={{ 
                        scale: [1, 1.1, 1],
                        filter: ["brightness(1)", "brightness(1.2)", "brightness(1)"] 
                      }}
                      transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                    >
                      <HiShieldCheck className="w-8 h-8 text-green-400" />
                    </motion.div>
                  </div>
                  <div className="flex items-center">
                    <Badge variant="outline" className="text-xs bg-green-500/10 text-green-400 border-green-500/20">
                      <CheckCircle className="w-3 h-3 mr-1" />All Systems Secure
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </motion.div>

          {/* Main Content Tabs */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 1.3 }}
          >
            <Tabs defaultValue="assets" className="space-y-6">
              <TabsList className="bg-card border-border">
              <TabsTrigger value="assets" className="data-[state=active]:bg-accent data-[state=active]:text-foreground text-muted-foreground">
                <GiHoneypot className="w-4 h-4 mr-2" />Assets
              </TabsTrigger>
              <TabsTrigger value="analytics" className="data-[state=active]:bg-accent data-[state=active]:text-foreground text-muted-foreground">
                <MdMonitorHeart className="w-4 h-4 mr-2" />Analytics
              </TabsTrigger>
              <TabsTrigger value="threats" className="data-[state=active]:bg-accent data-[state=active]:text-foreground text-muted-foreground">
                <MdBugReport className="w-4 h-4 mr-2" />Threat Log
              </TabsTrigger>
            </TabsList>

            <TabsContent value="assets">
              {/* Assets Table */}
              <Card className="bg-card border-border">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-foreground flex items-center">
                      <GiHoneypot className="w-5 h-5 mr-2" />
                      Honeypot Assets
                    </CardTitle>
                    <Button 
                      variant="outline" 
                      size="sm" 
                      className="border-border bg-transparent text-foreground hover:bg-accent hover:text-foreground"
                      onClick={() => setDeployDialogOpen(true)}
                    >
                      <FaRobot className="w-4 h-4 mr-2" />Deploy New
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="p-0">
                  {loading ? (
                    <div className="p-8 text-center text-muted-foreground">
                      <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-2" />
                      <p>Loading honeypots...</p>
                    </div>
                  ) : error ? (
                    <div className="p-8 text-center text-red-400">
                      <AlertTriangle className="w-8 h-8 mx-auto mb-2" />
                      <p>{error}</p>
                      <Button 
                        variant="outline" 
                        size="sm" 
                        onClick={fetchHoneypots}
                        className="mt-4 border-border text-foreground hover:bg-accent"
                      >
                        Try Again
                      </Button>
                    </div>
                  ) : honeypots.length === 0 ? (
                    <div className="p-8 text-center text-muted-foreground">
                      <GiHoneypot className="w-8 h-8 mx-auto mb-2 opacity-50" />
                      <p>No honeypots found</p>
                    </div>
                  ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b border-border">
                          <th className="text-left px-6 py-3 text-muted-foreground font-normal text-sm"></th>
                          <th className="text-left px-6 py-3 text-muted-foreground font-normal text-sm">Asset</th>
                          <th className="text-left px-6 py-3 text-muted-foreground font-normal text-sm">Status</th>
                          <th className="text-left px-6 py-3 text-muted-foreground font-normal text-sm">Threat Level</th>
                          <th className="text-left px-6 py-3 text-muted-foreground font-normal text-sm">Activity</th>
                          <th className="text-left px-6 py-3 text-muted-foreground font-normal text-sm">Interactions</th>
                          <th className="text-left px-6 py-3 text-muted-foreground font-normal text-sm">Protection</th>
                          <th className="text-left px-6 py-3 text-muted-foreground font-normal text-sm">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {honeypots.map((asset, index) => (
                          <motion.tr 
                            key={asset.id} 
                            className="border-b border-border"
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ 
                              duration: 0.3, 
                              delay: 1.4 + (index * 0.05),
                              backgroundColor: { duration: 0.3, ease: "easeInOut" }
                            }}
                            whileHover={{ 
                              backgroundColor: "rgba(55, 65, 81, 0.5)"
                            }}
                            style={{
                              backgroundColor: "transparent"
                            }}
                          >
                            <td className="px-6 py-4">
                              <Button variant="ghost" size="sm" className="p-0 h-auto" onClick={() => handleStarToggle(asset.id)}>
                                <Star className={`w-4 h-4 ${asset.starred ? 'fill-yellow-500 text-yellow-500' : 'text-muted-foreground'}`} />
                              </Button>
                            </td>
                            <td className="px-6 py-4">
                              <HoverCard>
                                <HoverCardTrigger asChild>
                                  <div className="flex items-center gap-3 cursor-pointer">
                                    <div className="w-8 h-8 bg-accent rounded-lg flex items-center justify-center">
                                      <GiHoneypot className="w-5 h-5 text-amber-400" />
                                    </div>
                                    <div>
                                      <p className="font-medium text-foreground">{asset.name}</p>
                                      <p className="text-sm text-muted-foreground font-mono">{asset.address}</p>
                                    </div>
                                  </div>
                                </HoverCardTrigger>
                                <HoverCardContent className="bg-accent border-border">
                                  <div className="space-y-2">
                                    <h4 className="text-sm font-semibold text-foreground">{asset.name} Honeypot</h4>
                                    <p className="text-xs text-muted-foreground">Address: {asset.address}</p>
                                    <p className="text-xs text-muted-foreground">Balance: {asset.balance} {asset.symbol}</p>
                                    <p className="text-xs text-muted-foreground">Last Activity: {asset.lastActivity}</p>
                                  </div>
                                </HoverCardContent>
                              </HoverCard>
                            </td>
                            <td className="px-6 py-4">
                              {getStatusBadge(asset.status)}
                            </td>
                            <td className="px-6 py-4">
                              <div className="space-y-2">
                                <div className="flex items-center gap-2">
                                  <span className={`text-sm font-medium ${getThreatLevelColor(asset.threatLevel)}`}>
                                    {asset.threatLevel.toUpperCase()}
                                  </span>
                                </div>
                                <Progress 
                                  value={getThreatProgress(asset.threatLevel)} 
                                  className="h-1 w-16"
                                />
                              </div>
                            </td>
                            <td className="px-6 py-4">
                              <div className={`flex items-center text-sm ${asset.change > 0 ? 'text-green-500' : asset.change < 0 ? 'text-red-500' : 'text-muted-foreground'}`}>
                                {asset.change > 0 ? <TrendingUp className="w-3 h-3 mr-1" /> : asset.change < 0 ? <TrendingDown className="w-3 h-3 mr-1" /> : <Wifi className="w-3 h-3 mr-1" />}
                                <span className="text-xs text-muted-foreground">{asset.lastActivity}</span>
                              </div>
                            </td>
                            <td className="px-6 py-4">
                              <Badge variant="outline" className="text-xs text-gray-300 border-gray-600">
                                {asset.interaction_count} events
                              </Badge>
                            </td>
                            <td className="px-6 py-4">
                              <Tooltip>
                                <TooltipTrigger asChild>
                                  <Badge 
                                    variant="secondary" 
                                    className={asset.protection === 'rsa' ? 'bg-orange-500/10 text-orange-400 border-orange-500/20' : 'bg-green-500/10 text-green-400 border-green-500/20'}
                                  >
                                    <Lock className="w-3 h-3 mr-1" />
                                    {asset.protection === 'rsa' ? 'RSA' : 'ECDSA'}
                                  </Badge>
                                </TooltipTrigger>
                                <TooltipContent>
                                  <p>{asset.protection === 'rsa' ? 'RSA-2048 Encryption' : 'ECDSA Encryption'}</p>
                                </TooltipContent>
                              </Tooltip>
                            </td>
                            <td className="px-6 py-4">
                              <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                  <Button variant="ghost" size="sm" className="text-muted-foreground hover:text-foreground">
                                    <MoreHorizontal className="w-4 h-4" />
                                  </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="end" className="bg-card border-border">
                                  <DropdownMenuItem 
                                    className="text-foreground hover:bg-accent focus:bg-accent focus:text-foreground cursor-pointer"
                                    onClick={() => setHoneypotDialogOpen(`details-${asset.id}`)}
                                  >
                                    <Eye className="w-4 h-4 mr-2" />View Details
                                  </DropdownMenuItem>
                                  <DropdownMenuItem 
                                    className="text-foreground hover:bg-accent focus:bg-accent focus:text-foreground cursor-pointer"
                                    onClick={() => setHoneypotDialogOpen(`configure-${asset.id}`)}
                                  >
                                    <Settings className="w-4 h-4 mr-2" />Configure
                                  </DropdownMenuItem>
                                  <DropdownMenuSeparator className="bg-secondary" />
                                  {asset.status === "disabled" ? (
                                    <DropdownMenuItem 
                                      className="text-green-400 hover:bg-accent focus:bg-accent focus:text-green-400 cursor-pointer"
                                      onClick={() => setHoneypotDialogOpen(`enable-${asset.id}`)}
                                    >
                                      <CheckCircle className="w-4 h-4 mr-2" />Enable
                                    </DropdownMenuItem>
                                  ) : (
                                    <DropdownMenuItem 
                                      className="text-red-400 hover:bg-accent focus:bg-accent focus:text-red-400 cursor-pointer"
                                      onClick={() => setHoneypotDialogOpen(`disable-${asset.id}`)}
                                    >
                                      <XCircle className="w-4 h-4 mr-2" />Disable
                                    </DropdownMenuItem>
                                  )}
                                  <DropdownMenuSeparator className="bg-secondary" />
                                  <DropdownMenuItem 
                                    className="text-red-400 hover:bg-accent focus:bg-accent focus:text-red-400 cursor-pointer"
                                    onClick={() => setHoneypotDialogOpen(`delete-${asset.id}`)}
                                  >
                                    <Trash2 className="w-4 h-4 mr-2" />Delete
                                  </DropdownMenuItem>
                                </DropdownMenuContent>
                              </DropdownMenu>
                            </td>
                          </motion.tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="analytics">
              <Card className="bg-card border-border">
                <CardHeader>
                  <CardTitle className="text-foreground">Analytics Dashboard</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-12 text-muted-foreground">
                    <MdMonitorHeart className="w-16 h-16 mx-auto mb-4 opacity-50" />
                    <p>Analytics dashboard coming soon...</p>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="threats">
              <Card className="bg-card border-border">
                <CardHeader>
                  <CardTitle className="text-foreground flex items-center">
                    <MdBugReport className="w-5 h-5 mr-2 text-red-400" />
                    Threat Detection Log
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <Alert className="bg-red-500/10 border-red-500/20">
                      <MdBugReport className="h-4 w-4 text-red-400" />
                      <AlertDescription className="text-red-200">
                        <strong>High Priority:</strong> Quantum Token honeypot detected suspicious activity (1 minute ago)
                      </AlertDescription>
                    </Alert>
                    <Alert className="bg-yellow-500/10 border-yellow-500/20">
                      <MdBugReport className="h-4 w-4 text-yellow-400" />
                      <AlertDescription className="text-yellow-200">
                        <strong>Medium Priority:</strong> Bitcoin honeypot triggered - 3 interactions detected (5 minutes ago)
                      </AlertDescription>
                    </Alert>
                    <Alert className="bg-blue-500/10 border-blue-500/20">
                      <MdRadar className="h-4 w-4 text-blue-400" />
                      <AlertDescription className="text-blue-200">
                        <strong>Info:</strong> Ethereum honeypot monitoring active (2 hours ago)
                      </AlertDescription>
                    </Alert>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
          </motion.div>
        </div>
      </motion.div>

      {/* Configure Alerts Dialog */}
      <Dialog open={alertsDialogOpen} onOpenChange={setAlertsDialogOpen}>
        <DialogContent className="bg-card border-border text-foreground max-w-md">
          <DialogHeader>
            <DialogTitle className="text-foreground flex items-center">
              <AlertTriangle className="w-5 h-5 mr-2 text-red-400" />
              Configure Alerts
            </DialogTitle>
            <DialogDescription className="text-muted-foreground">
              Set up alert preferences for threat detection and monitoring.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-foreground">Email Alerts</label>
                <p className="text-xs text-muted-foreground">Receive email notifications for threats</p>
              </div>
              <Switch 
                checked={settings.emailAlerts}
                onCheckedChange={(checked) => setSettings(prev => ({ ...prev, emailAlerts: checked }))}
                className="data-[state=checked]:bg-green-600 data-[state=unchecked]:bg-gray-600 border-gray-500"
              />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-foreground">Auto Response</label>
                <p className="text-xs text-muted-foreground">Automatically respond to detected threats</p>
              </div>
              <Switch 
                checked={settings.autoResponse}
                onCheckedChange={(checked) => setSettings(prev => ({ ...prev, autoResponse: checked }))}
                className="data-[state=checked]:bg-green-600 data-[state=unchecked]:bg-gray-600 border-gray-500"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Threat Threshold</label>
              <Select value={settings.threatThreshold} onValueChange={(value) => setSettings(prev => ({ ...prev, threatThreshold: value }))}>
                <SelectTrigger className="bg-accent border-border text-foreground">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-accent border-border">
                  <SelectItem value="low" className="text-foreground">Low - Alert on all activities</SelectItem>
                  <SelectItem value="medium" className="text-foreground">Medium - Alert on suspicious activities</SelectItem>
                  <SelectItem value="high" className="text-foreground">High - Alert only on confirmed threats</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setAlertsDialogOpen(false)} className="border-gray-600 bg-accent text-gray-300 hover:bg-accent hover:text-foreground hover:border-gray-500">
              Cancel
            </Button>
            <Button onClick={handleUpdateSettings} className="bg-secondary hover:bg-gray-600 text-foreground border border-gray-600">
              Save Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Notification Settings Dialog */}
      <Dialog open={notificationDialogOpen} onOpenChange={setNotificationDialogOpen}>
        <DialogContent className="bg-card border-border text-foreground max-w-md">
          <DialogHeader>
            <DialogTitle className="text-foreground flex items-center">
              <MdMonitorHeart className="w-5 h-5 mr-2 text-blue-400" />
              Notification Settings
            </DialogTitle>
            <DialogDescription className="text-muted-foreground">
              Manage how and when you receive notifications.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-foreground">Push Notifications</label>
                <p className="text-xs text-muted-foreground">Receive browser push notifications</p>
              </div>
              <Switch 
                checked={settings.pushNotifications}
                onCheckedChange={(checked) => setSettings(prev => ({ ...prev, pushNotifications: checked }))}
                className="data-[state=checked]:bg-green-600 data-[state=unchecked]:bg-gray-600 border-gray-500"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Monitoring Interval (minutes)</label>
              <Input 
                type="number"
                value={settings.monitoringInterval}
                onChange={(e) => setSettings(prev => ({ ...prev, monitoringInterval: e.target.value }))}
                className="bg-accent border-border text-foreground"
                min="1"
                max="60"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Data Retention (days)</label>
              <Input 
                type="number"
                value={settings.retentionPeriod}
                onChange={(e) => setSettings(prev => ({ ...prev, retentionPeriod: e.target.value }))}
                className="bg-accent border-border text-foreground"
                min="1"
                max="365"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setNotificationDialogOpen(false)} className="border-gray-600 bg-accent text-gray-300 hover:bg-accent hover:text-foreground hover:border-gray-500">
              Cancel
            </Button>
            <Button onClick={handleUpdateSettings} className="bg-secondary hover:bg-gray-600 text-foreground border border-gray-600">
              Save Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Advanced Settings Dialog */}
      <Dialog open={advancedDialogOpen} onOpenChange={setAdvancedDialogOpen}>
        <DialogContent className="bg-card border-border text-foreground max-w-md">
          <DialogHeader>
            <DialogTitle className="text-foreground flex items-center">
              <HiCpuChip className="w-5 h-5 mr-2 text-purple-400" />
              Advanced Settings
            </DialogTitle>
            <DialogDescription className="text-muted-foreground">
              Configure advanced security and routing features.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Routing Method</label>
              <Select defaultValue="classical">
                <SelectTrigger className="bg-accent border-border text-foreground">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-accent border-border">
                  <SelectItem value="classical" className="text-foreground">Classical - Standard routing</SelectItem>
                  <SelectItem value="post_quantum" className="text-foreground">Post-Quantum - When threats detected</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Default Encryption</label>
              <Select defaultValue="ecdsa">
                <SelectTrigger className="bg-accent border-border text-foreground">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-accent border-border">
                  <SelectItem value="rsa" className="text-foreground">RSA-2048</SelectItem>
                  <SelectItem value="ecdsa" className="text-foreground">ECDSA (Recommended)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg">
              <p className="text-xs text-blue-200">
                <strong>Info:</strong> The system will automatically switch to post-quantum routing when threats are detected.
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setAdvancedDialogOpen(false)} className="border-gray-600 bg-accent text-gray-300 hover:bg-accent hover:text-foreground hover:border-gray-500">
              Cancel
            </Button>
            <Button onClick={handleUpdateSettings} className="bg-secondary hover:bg-gray-600 text-foreground border border-gray-600">
              Apply Settings
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Honeypot Action Dialogs */}
      {honeypots.map((asset) => (
        <React.Fragment key={asset.id}>
          {/* View Details Dialog */}
          <Dialog open={honeypotDialogOpen === `details-${asset.id}`} onOpenChange={(open) => !open && setHoneypotDialogOpen(null)}>
            <DialogContent className="bg-card border-border text-foreground max-w-lg">
              <DialogHeader>
                <DialogTitle className="text-foreground flex items-center">
                  <GiHoneypot className="w-5 h-5 mr-2 text-amber-400" />
                  {asset.name} Details
                </DialogTitle>
                <DialogDescription className="text-muted-foreground">
                  Detailed information about this honeypot asset.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs text-muted-foreground">Asset Type</label>
                    <p className="text-sm text-foreground">{asset.name} ({asset.symbol})</p>
                  </div>
                  <div>
                    <label className="text-xs text-muted-foreground">Status</label>
                    <div className="mt-1">{getStatusBadge(asset.status)}</div>
                  </div>
                  <div>
                    <label className="text-xs text-muted-foreground">Address</label>
                    <p className="text-sm text-foreground font-mono">{asset.address}</p>
                  </div>
                  <div>
                    <label className="text-xs text-muted-foreground">Balance</label>
                    <p className="text-sm text-foreground">{asset.balance} {asset.symbol}</p>
                  </div>
                  <div>
                    <label className="text-xs text-muted-foreground">Threat Level</label>
                    <p className={`text-sm font-medium ${getThreatLevelColor(asset.threatLevel)}`}>
                      {asset.threatLevel.toUpperCase()}
                    </p>
                  </div>
                  <div>
                    <label className="text-xs text-muted-foreground">Interactions</label>
                    <p className="text-sm text-foreground">{asset.interactions} events</p>
                  </div>
                </div>
                <div>
                  <label className="text-xs text-muted-foreground">Protection Level</label>
                  <Badge 
                    className={asset.protection === 'rsa' ? 'bg-orange-500/10 text-orange-400 border-orange-500/20 mt-1' : 'bg-green-500/10 text-green-400 border-green-500/20 mt-1'}
                  >
                    <Lock className="w-3 h-3 mr-1" />
                    {asset.protection === 'rsa' ? 'RSA-2048 Encryption' : 'ECDSA Encryption'}
                  </Badge>
                </div>
                <div>
                  <label className="text-xs text-muted-foreground">Last Activity</label>
                  <p className="text-sm text-foreground">{asset.lastActivity}</p>
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setHoneypotDialogOpen(null)} className="border-gray-600 bg-accent text-gray-300 hover:bg-accent hover:text-foreground hover:border-gray-500">
                  Close
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>

          {/* Configure Dialog */}
          <Dialog open={honeypotDialogOpen === `configure-${asset.id}`} onOpenChange={(open) => !open && setHoneypotDialogOpen(null)}>
            <DialogContent className="bg-card border-border text-foreground max-w-md">
              <DialogHeader>
                <DialogTitle className="text-foreground flex items-center">
                  <Settings className="w-5 h-5 mr-2 text-blue-400" />
                  Configure {asset.name}
                </DialogTitle>
                <DialogDescription className="text-muted-foreground">
                  Adjust settings for this honeypot.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-foreground">Monitoring Sensitivity</label>
                  <Select 
                    value={configForm[asset.id]?.monitoring_sensitivity || asset.threatLevel}
                    onValueChange={(value) => setConfigForm(prev => ({
                      ...prev,
                      [asset.id]: {
                        ...prev[asset.id],
                        monitoring_sensitivity: value
                      }
                    }))}
                  >
                    <SelectTrigger className="bg-accent border-border text-foreground">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-accent border-border">
                      <SelectItem value="low" className="text-foreground">Low Sensitivity</SelectItem>
                      <SelectItem value="medium" className="text-foreground">Medium Sensitivity</SelectItem>
                      <SelectItem value="high" className="text-foreground">High Sensitivity</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-foreground">Protection Type</label>
                  <Select 
                    value={configForm[asset.id]?.protection_type || asset.protection}
                    onValueChange={(value) => setConfigForm(prev => ({
                      ...prev,
                      [asset.id]: {
                        ...prev[asset.id],
                        protection_type: value
                      }
                    }))}
                  >
                    <SelectTrigger className="bg-accent border-border text-foreground">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-accent border-border">
                      <SelectItem value="rsa" className="text-foreground">RSA-2048</SelectItem>
                      <SelectItem value="ecdsa" className="text-foreground">ECDSA</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <label className="text-sm font-medium text-foreground">Auto-Response</label>
                    <p className="text-xs text-muted-foreground">Automatically respond to threats</p>
                  </div>
                  <Switch 
                    checked={configForm[asset.id]?.auto_response ?? true}
                    onCheckedChange={(checked) => setConfigForm(prev => ({
                      ...prev,
                      [asset.id]: {
                        ...prev[asset.id],
                        auto_response: checked
                      }
                    }))}
                    className="data-[state=checked]:bg-green-600 data-[state=unchecked]:bg-gray-600 border-gray-500"
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setHoneypotDialogOpen(null)} className="border-gray-600 bg-accent text-gray-300 hover:bg-accent hover:text-foreground hover:border-gray-500">
                  Cancel
                </Button>
                <Button onClick={() => {
                  const config = {
                    monitoring_sensitivity: configForm[asset.id]?.monitoring_sensitivity || asset.threatLevel || 'medium',
                    protection_type: configForm[asset.id]?.protection_type || asset.protection || 'ecdsa',
                    auto_response: configForm[asset.id]?.auto_response ?? true,
                    routing_method: 'classical'
                  };
                  handleConfigureHoneypot(asset.id, config);
                }} className="bg-secondary hover:bg-gray-600 text-foreground border border-gray-600">
                  Save Changes
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>

          {/* Disable Dialog */}
          <Dialog open={honeypotDialogOpen === `disable-${asset.id}`} onOpenChange={(open) => !open && setHoneypotDialogOpen(null)}>
            <DialogContent className="bg-card border-border text-foreground max-w-md">
              <DialogHeader>
                <DialogTitle className="text-foreground flex items-center">
                  <XCircle className="w-5 h-5 mr-2 text-red-400" />
                  Disable {asset.name}
                </DialogTitle>
                <DialogDescription className="text-muted-foreground">
                  Are you sure you want to disable this honeypot? This action can be reversed later.
                </DialogDescription>
              </DialogHeader>
              <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                <p className="text-sm text-red-200">
                  <strong>Warning:</strong> Disabling this honeypot will stop all monitoring and threat detection for this asset.
                </p>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setHoneypotDialogOpen(null)} className="border-gray-600 bg-accent text-gray-300 hover:bg-accent hover:text-foreground hover:border-gray-500">
                  Cancel
                </Button>
                <Button onClick={() => handleDisableHoneypot(asset.id)} className="bg-red-800 hover:bg-red-700 text-red-100 border border-red-700">
                  Disable Honeypot
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>

          {/* Enable Dialog */}
          <Dialog open={honeypotDialogOpen === `enable-${asset.id}`} onOpenChange={(open) => !open && setHoneypotDialogOpen(null)}>
            <DialogContent className="bg-card border-border text-foreground max-w-md">
              <DialogHeader>
                <DialogTitle className="text-foreground flex items-center">
                  <CheckCircle className="w-5 h-5 mr-2 text-green-400" />
                  Enable {asset.name}
                </DialogTitle>
                <DialogDescription className="text-muted-foreground">
                  Are you sure you want to enable this honeypot? This will resume all monitoring and threat detection.
                </DialogDescription>
              </DialogHeader>
              <div className="p-3 bg-green-500/10 border border-green-500/20 rounded-lg">
                <p className="text-sm text-green-200">
                  <strong>Info:</strong> Enabling this honeypot will resume monitoring and threat detection for this asset.
                </p>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setHoneypotDialogOpen(null)} className="border-gray-600 bg-accent text-gray-300 hover:bg-accent hover:text-foreground hover:border-gray-500">
                  Cancel
                </Button>
                <Button onClick={() => handleEnableHoneypot(asset.id)} className="bg-green-800 hover:bg-green-700 text-green-100 border border-green-700">
                  Enable Honeypot
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>

          {/* Delete Dialog */}
          <Dialog open={honeypotDialogOpen === `delete-${asset.id}`} onOpenChange={(open) => !open && setHoneypotDialogOpen(null)}>
            <DialogContent className="bg-card border-border text-foreground max-w-md">
              <DialogHeader>
                <DialogTitle className="text-foreground flex items-center">
                  <Trash2 className="w-5 h-5 mr-2 text-red-400" />
                  Delete {asset.name}
                </DialogTitle>
                <DialogDescription className="text-muted-foreground">
                  Are you sure you want to permanently delete this honeypot? This action cannot be undone.
                </DialogDescription>
              </DialogHeader>
              <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                <p className="text-sm text-red-200">
                  <strong>Warning:</strong> Deleting this honeypot will permanently remove all configuration, monitoring data, and historical records. This action cannot be reversed.
                </p>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setHoneypotDialogOpen(null)} className="border-gray-600 bg-accent text-gray-300 hover:bg-accent hover:text-foreground hover:border-gray-500">
                  Cancel
                </Button>
                <Button onClick={() => handleDeleteHoneypot(asset.id)} className="bg-red-900 hover:bg-red-800 text-red-100 border border-red-800">
                  Delete Permanently
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </React.Fragment>
      ))}

      {/* Deploy New Honeypot Dialog */}
      <Dialog open={deployDialogOpen} onOpenChange={setDeployDialogOpen}>
        <DialogContent className="bg-card border-border text-foreground max-w-md">
          <DialogHeader>
            <DialogTitle className="text-foreground flex items-center">
              <FaRobot className="w-5 h-5 mr-2 text-blue-400" />
              Deploy New Honeypot
            </DialogTitle>
            <DialogDescription className="text-muted-foreground">
              Configure and deploy a new honeypot to strengthen your security posture.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Honeypot Name *</label>
              <Input 
                value={deployForm.name}
                onChange={(e) => setDeployForm(prev => ({...prev, name: e.target.value}))}
                placeholder="e.g., Quantum Honeypot 4"
                className="bg-accent border-border text-foreground placeholder:text-gray-500"
              />
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Blockchain Network</label>
              <Select 
                value={deployForm.blockchain}
                onValueChange={(value) => setDeployForm(prev => ({...prev, blockchain: value}))}
              >
                <SelectTrigger className="bg-accent border-border text-foreground">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-accent border-border">
                  <SelectItem value="ethereum" className="text-foreground">
                    <div className="flex items-center">
                      <SiEthereum className="w-4 h-4 mr-2 text-blue-400" />
                      Ethereum
                    </div>
                  </SelectItem>
                  <SelectItem value="bitcoin" disabled className="text-muted-foreground opacity-50">
                    <div className="flex items-center">
                      <SiBitcoin className="w-4 h-4 mr-2 text-orange-400" />
                      Bitcoin (Coming Soon)
                    </div>
                  </SelectItem>
                  <SelectItem value="quantum" disabled className="text-muted-foreground opacity-50">
                    <div className="flex items-center">
                      <HiCpuChip className="w-4 h-4 mr-2 text-purple-400" />
                      Quantum Testnet (Coming Soon)
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Protection Type</label>
              <Select 
                value={deployForm.protection_type}
                onValueChange={(value) => setDeployForm(prev => ({...prev, protection_type: value}))}
              >
                <SelectTrigger className="bg-accent border-border text-foreground">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-accent border-border">
                  <SelectItem value="rsa" className="text-foreground">RSA-2048</SelectItem>
                  <SelectItem value="ecdsa" className="text-foreground">ECDSA</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Monitoring Sensitivity</label>
              <Select 
                value={deployForm.monitoring_sensitivity}
                onValueChange={(value) => setDeployForm(prev => ({...prev, monitoring_sensitivity: value}))}
              >
                <SelectTrigger className="bg-accent border-border text-foreground">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-accent border-border">
                  <SelectItem value="low" className="text-foreground">Low Sensitivity</SelectItem>
                  <SelectItem value="medium" className="text-foreground">Medium Sensitivity</SelectItem>
                  <SelectItem value="high" className="text-foreground">High Sensitivity</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Description</label>
              <Input 
                value={deployForm.description}
                onChange={(e) => setDeployForm(prev => ({...prev, description: e.target.value}))}
                placeholder="Optional description for this honeypot"
                className="bg-accent border-border text-foreground placeholder:text-gray-500"
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-foreground">Auto-Response</label>
                <p className="text-xs text-muted-foreground">Automatically respond to detected threats</p>
              </div>
              <Switch 
                checked={deployForm.auto_response}
                onCheckedChange={(checked) => setDeployForm(prev => ({...prev, auto_response: checked}))}
                className="data-[state=checked]:bg-green-600 data-[state=unchecked]:bg-gray-600 border-gray-500"
              />
            </div>
          </div>
          
          <DialogFooter>
            <Button 
              variant="outline" 
              onClick={() => setDeployDialogOpen(false)} 
              className="border-gray-600 bg-accent text-gray-300 hover:bg-accent hover:text-foreground hover:border-gray-500"
            >
              Cancel
            </Button>
            <Button 
              onClick={handleDeployHoneypot}
              disabled={!deployForm.name.trim()}
              className="bg-blue-700 hover:bg-blue-600 text-foreground border border-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Deploy Honeypot
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </TooltipProvider>

  )
}