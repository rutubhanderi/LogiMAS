import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Plus, MoreHorizontal } from 'lucide-react';

export default function KnowledgeBasePage() {
  const documents = Array(6).fill("Document Name");

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Knowledge Base</h1>
        <Button>
          <Plus className="mr-2 h-4 w-4" /> New
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {documents.map((name, index) => (
          <Card key={index}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">{name}</CardTitle>
              <MoreHorizontal className="h-4 w-4 text-muted-foreground cursor-pointer" />
            </CardHeader>
            <CardContent>
              <div className="aspect-square bg-secondary rounded-md">
                {/* Placeholder for document preview */}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}