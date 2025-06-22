import * as React from "react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { 
  Home,
  ArrowUpDown,
  Wallet,
  BarChart3,
  Settings
} from "lucide-react"

interface SidebarProps extends React.HTMLAttributes<HTMLDivElement> {}

const menuItems = [
  {
    title: "Home",
    icon: Home,
    href: "/",
  },
  {
    title: "Trade", 
    icon: ArrowUpDown,
    href: "/trade",
  },
  {
    title: "Assets",
    icon: Wallet,
    href: "/assets",
    active: true
  },
  {
    title: "Analytics",
    icon: BarChart3,
    href: "/analytics"
  }
]

export function Sidebar({ className, ...props }: SidebarProps) {
  return (
    <div className={cn("w-16 bg-gray-950/60 border-r border-gray-800", className)} {...props}>
      <div className="flex flex-col h-full">
        <div className="p-4">
          {/* Logo removed for now */}
        </div>
        
        <nav className="flex-1 px-2">
          {menuItems.map((item) => (
            <Button
              key={item.href}
              variant="ghost"
              size="icon"
              className={cn(
                "w-12 h-12 mb-1",
                item.active 
                  ? "text-white bg-gray-800" 
                  : "text-gray-400 hover:text-white hover:bg-gray-800"
              )}
            >
              <item.icon className="h-5 w-5" />
            </Button>
          ))}
        </nav>
        
        <div className="p-2 border-t border-gray-800">
          <Button variant="ghost" size="icon" className="w-12 h-12 text-gray-400 hover:text-white hover:bg-gray-800">
            <Settings className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </div>
  )
}