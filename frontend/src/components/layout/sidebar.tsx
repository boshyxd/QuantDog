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
    <div className={cn("w-16 bg-[#313244] border-r border-[#7f849c]", className)} {...props}>
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
                  ? "text-[#cdd6f4] bg-[#45475a]" 
                  : "text-[#a6adc8] hover:text-[#cdd6f4] hover:bg-[#45475a]"
              )}
            >
              <item.icon className="h-5 w-5" />
            </Button>
          ))}
        </nav>
        
        <div className="p-2 border-t border-[#7f849c]">
          <Button variant="ghost" size="icon" className="w-12 h-12 text-[#a6adc8] hover:text-[#cdd6f4] hover:bg-[#45475a]">
            <Settings className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </div>
  )
}