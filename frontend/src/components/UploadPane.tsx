import { useState } from "react";
import { Card } from "@/components/ui/card";
import YouTubeInput from "./YouTubeInput";
import UserContext from "./UserContext";
import ContentExtractor from "./ContentExtractor";
import { useToast } from "@/hooks/use-toast";
import { UserContext as UserContextType } from "@/lib/api";

interface UploadPaneProps {
  onContentProcessed: (content: string) => void;
  setIsProcessing: (isProcessing: boolean) => void;
}

const UploadPane = ({ onContentProcessed, setIsProcessing }: UploadPaneProps) => {
  const { toast } = useToast();
  const [files, setFiles] = useState<File[]>([]);
  const [youtubeUrl, setYoutubeUrl] = useState<string>("");
  const [userInfo, setUserInfo] = useState<UserContextType>({
    interests: "",
    goals: "",
    background: ""
  });

  const handleYoutubeChange = (url: string) => {
    setYoutubeUrl(url);
  };

  const handleUserInfoChange = (info: UserContextType) => {
    setUserInfo(info);
  };

  const handleProcessStart = () => {
    toast({
      title: "Processing content",
      description: "Extracting insights and generating your personalized prompt...",
    });
  };

  return (
    <div className="space-y-8">
      <div className="mb-4">
        <h2 className="text-2xl font-semibold mb-6">Content Source</h2>
        <Card className="p-6 shadow-md border-border bg-card">
          <YouTubeInput onUrlChange={handleYoutubeChange} />
        </Card>
      </div>
      
      <div>
        <div className="flex items-center gap-2 mb-6">
          <h2 className="text-2xl font-semibold">About You</h2>
          <span className="text-sm text-muted-foreground">(optional)</span>
        </div>
        <Card className="p-6 shadow-md border-border bg-card">
          <UserContext onChange={handleUserInfoChange} />
        </Card>
      </div>
      
      <ContentExtractor 
        files={files} 
        youtubeUrl={youtubeUrl}
        userInfo={userInfo}
        onProcess={handleProcessStart}
        onContentProcessed={onContentProcessed}
        setIsProcessing={setIsProcessing}
      />
    </div>
  );
};

export default UploadPane;
