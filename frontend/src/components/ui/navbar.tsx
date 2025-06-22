import * as React from "react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { 
  Bell, 
  Search, 
  User, 
  Cpu, 
  Wifi,
  Shield,
  AlertCircle
} from "lucide-react"

interface NavbarProps extends React.HTMLAttributes<HTMLDivElement> {}

export function Navbar({ className, ...props }: NavbarProps) {
  return (
    <div className={cn("h-16 bg-black/95 border-b border-green-500/20 backdrop-blur-sm", className)} {...props}>
      <div className="flex items-center justify-between h-full px-6">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-sm font-mono text-green-400">SYSTEM ONLINE</span>
          </div>
          
          <div className="h-4 w-px bg-green-500/20"></div>
          
          <div className="flex items-center gap-2 text-xs font-mono text-gray-400">
            <Cpu className="w-3 h-3" />
            <span>QUANTUM ENGINE: READY</span>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-3 py-1 bg-yellow-500/10 border border-yellow-500/20 rounded-md">
            <AlertCircle className="w-4 h-4 text-yellow-400" />
            <span className="text-xs font-mono text-yellow-400">THREAT: MEDIUM</span>
          </div>
          
          <div className="flex items-center gap-2 px-3 py-1 bg-green-500/10 border border-green-500/20 rounded-md">
            <Shield className="w-4 h-4 text-green-400" />
            <span className="text-xs font-mono text-green-400">PROTECTED</span>
          </div>
          
          <div className="h-4 w-px bg-green-500/20"></div>
          
          <Button variant="ghost" size="sm" className="text-gray-400 hover:text-green-400">
            <Search className="w-4 h-4" />
          </Button>
          
          <Button variant="ghost" size="sm" className="text-gray-400 hover:text-green-400 relative">
            <Bell className="w-4 h-4" />
            <div className="absolute -top-1 -right-1 w-2 h-2 bg-red-400 rounded-full"></div>
          </Button>
          
          <Button variant="ghost" size="sm" className="text-gray-400 hover:text-green-400">
            <User className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}