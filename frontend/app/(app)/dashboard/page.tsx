import { Input } from "@/components/ui/input";
import { Truck, ShoppingCart, CircleDollarSign, CornerDownLeft, Copy } from 'lucide-react';

export default function DashboardPage() {
  return (
    <div className="h-full flex flex-col items-center justify-center">
      <div className="w-full max-w-3xl text-center">
        <h1 className="text-4xl font-bold text-foreground mb-8">
          Hello Rutu, what quest are we on today?
        </h1>
        <div className="relative">
          <Input 
            placeholder="Type here..."
            className="h-14 text-lg bg-secondary pl-6 pr-24"
          />
          <div className="absolute inset-y-0 right-4 flex items-center space-x-3">
             <CornerDownLeft className="h-5 w-5 text-muted-foreground" />
             <Copy className="h-5 w-5 text-muted-foreground" />
          </div>
        </div>
        <div className="mt-6 flex justify-center space-x-6">
          <Truck className="h-8 w-8 text-muted-foreground cursor-pointer hover:text-primary" />
          <ShoppingCart className="h-8 w-8 text-muted-foreground cursor-pointer hover:text-primary" />
          <CircleDollarSign className="h-8 w-8 text-muted-foreground cursor-pointer hover:text-primary" />
        </div>
      </div>
    </div>
  );
}