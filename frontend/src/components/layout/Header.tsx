import { ThemeToggle } from "@/components/theme/ThemeToggle";

const Header = () => {
  return (
    <header className="h-20 border-b flex items-center justify-between px-6 bg-background">
      <div className="flex items-center gap-2">
        <img 
          src="/introspect-icon.png" 
          alt="IntrospectAI" 
          className="h-8 w-8 md:hidden"
        />
        <img 
          src="/introspect-logo.png" 
          alt="IntrospectAI" 
          className="h-12 hidden md:block"
        />
      </div>
      <ThemeToggle />
    </header>
  );
};

export default Header; 