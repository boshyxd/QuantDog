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
    <div className={cn("w-16 bg-sidebar border-r border-sidebar-border", className)} {...props}>
      <div className="flex flex-col h-full">
        <div className="p-4 flex justify-center">
          <img src="/logo.svg" alt="QuantDog" className="w-8 h-8" />
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
                  ? "text-sidebar-foreground bg-sidebar-accent" 
                  : "text-muted-foreground hover:text-sidebar-foreground hover:bg-sidebar-accent"
              )}
            >
              <item.icon className="h-6 w-6" />
            </Button>
          ))}
        </nav>
        
        <div className="p-2 border-t border-sidebar-border">
          <Button variant="ghost" size="icon" className="w-12 h-12 text-muted-foreground hover:text-sidebar-foreground hover:bg-sidebar-accent">
            <Settings className="h-6 w-6" />
          </Button>
        </div>
      </div>
    </div>
  )
}