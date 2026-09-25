export function Header() {
  return (
    <header className="h-14 border-b border-border bg-card flex items-center px-6 justify-between">
      <div className="flex items-center">
        <h1 className="text-sm font-medium text-mutedForeground">Security Operations Center</h1>
      </div>
      <div className="flex items-center space-x-4">
        <div className="text-sm text-mutedForeground">
          System Status: <span className="text-green-500 font-medium">Online</span>
        </div>
      </div>
    </header>
  );
}
