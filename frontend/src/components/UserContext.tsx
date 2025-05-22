
import { useState } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";

interface UserContextProps {
  onChange: (info: {
    interests: string;
    goals: string;
    background: string;
  }) => void;
}

const UserContext = ({ onChange }: UserContextProps) => {
  const [interests, setInterests] = useState("");
  const [goals, setGoals] = useState("");
  const [background, setBackground] = useState("");

  const handleInterestsChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInterests(e.target.value);
    updateParent(e.target.value, goals, background);
  };

  const handleGoalsChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setGoals(e.target.value);
    updateParent(interests, e.target.value, background);
  };

  const handleBackgroundChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setBackground(e.target.value);
    updateParent(interests, goals, e.target.value);
  };

  const updateParent = (
    interests: string,
    goals: string,
    background: string
  ) => {
    onChange({
      interests,
      goals,
      background,
    });
  };

  return (
    <Card className="p-6 shadow-lg border-blue-100">
      <div className="space-y-6">
        <div className="space-y-2">
          <label htmlFor="interests" className="block text-sm font-medium">
            What are your interests and hobbies?
          </label>
          <Textarea
            id="interests"
            placeholder="e.g., web development, gardening, history, fitness..."
            value={interests}
            onChange={handleInterestsChange}
            className="min-h-[80px]"
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="goals" className="block text-sm font-medium">
            What are your current goals?
          </label>
          <Textarea
            id="goals"
            placeholder="e.g., learn a new skill, improve productivity, start a business..."
            value={goals}
            onChange={handleGoalsChange}
            className="min-h-[80px]"
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="background" className="block text-sm font-medium">
            Relevant background (optional)
          </label>
          <Textarea
            id="background"
            placeholder="e.g., your profession, education, life situation..."
            value={background}
            onChange={handleBackgroundChange}
            className="min-h-[80px]"
          />
        </div>
      </div>
    </Card>
  );
};

export default UserContext;
