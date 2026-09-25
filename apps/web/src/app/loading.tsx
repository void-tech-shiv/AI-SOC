import { Loader2 } from "lucide-react";

export default function Loading() {
  return (
    <div className="flex items-center justify-center h-[50vh] w-full">
      <div className="flex flex-col items-center gap-4 text-mutedForeground">
        <Loader2 className="h-8 w-8 animate-spin" />
        <p>Loading data...</p>
      </div>
    </div>
  );
}
