import * as React from "react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import GooeyNav from "@/components/blocks/Components/GooeyNav/GooeyNav"
import { 
  Search,
  ChevronDown
} from "lucide-react"

interface NavbarProps extends React.HTMLAttributes<HTMLDivElement> {}

const navItems = [
  { label: "Honeypots", href: "#" },
  { label: "Monitoring", href: "#" },
  { label: "Security", href: "#" }
]

export function Navbar({ className, ...props }: NavbarProps) {
  return (
    <div className={cn("h-16 bg-gray-950/80 border-b border-gray-800", className)} {...props}>
      <div className="flex items-center justify-between h-full px-4">
        <div className="flex items-center gap-6">
          <h1 className="text-xl font-semibold text-white">Assets</h1>
          
          <div className="hidden md:flex items-center" style={{ height: '50px', position: 'relative' }}>
            <GooeyNav
              items={navItems}
              particleCount={15}
              particleDistances={[90, 10]}
              particleR={100}
              initialActiveIndex={0}
              animationTime={600}
              timeVariance={300}
              colors={[1, 2, 3, 1, 2, 3, 1, 4]}
            />
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="relative hidden md:block">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search"
              className="pl-10 pr-4 py-2 bg-gray-900 border border-gray-800 rounded-lg text-sm text-white placeholder-gray-400 focus:outline-none focus:border-gray-700"
            />
          </div>
          
          <Button className="bg-gray-800 hover:bg-gray-700 text-white border border-gray-700">
            Deploy Honeypot
          </Button>
          
          <Button variant="ghost" size="sm" className="text-gray-400 hover:text-white hover:bg-gray-800">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gray-800 rounded-full"></div>
              <ChevronDown className="h-4 w-4" />
            </div>
          </Button>
        </div>
      </div>
    </div>
  )
}