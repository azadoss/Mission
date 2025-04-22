import React, { useState, useEffect, useRef } from "react";
import { Input } from "./ui/input";
import { Button } from "./ui/button";
import { ScrollArea } from "./ui/scroll-area";
import { Avatar } from "./ui/avatar";
import { AvatarImage } from "@radix-ui/react-avatar";
import { useWebSocket } from "./WebSocketProvider";
import { Card, CardHeader, CardTitle, CardContent } from "./ui/card";

export interface Message {
  text: string;
  sender: "User" | "Gemini";
  timestamp: string;
  isComplete: boolean;
  type: "text";
}

const Chat: React.FC = () => {
  const [inputText, setInputText] = useState("");
  const { sendMessage, lastTranscription } = useWebSocket();
  const [messages, setMessages] = useState<Message[]>([
    {
      text: "Screen sharing session started. I'll transcribe what I see.",
      sender: "Gemini",
      timestamp: new Date().toLocaleTimeString(),
      isComplete: true,
      type: "text",
    },
  ]);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputText(e.target.value);
  };

  const handleSendMessage = () => {
    const text = inputText.trim();
    if (!text) return;
    const now = new Date().toLocaleTimeString();
    setMessages(prev => [
      ...prev,
      { text, sender: "User", timestamp: now, isComplete: true, type: "text" },
    ]);
    sendMessage({ type: "text", data: { text } });
    setInputText("");
  };

  const pendingRef = useRef<string>("");
  const debounceRef = useRef<NodeJS.Timeout>();

  const commitTranscription = (text: string, isComplete: boolean) => {
    setMessages(prev => {
      const lastIndex = prev.length - 1;
      const lastMsg = prev[lastIndex];
      const isSame = lastMsg && lastMsg.sender === "Gemini" && lastMsg.type === "text" && !lastMsg.isComplete;

      if (isSame) {
        const updated = [...prev];
        updated[lastIndex] = {
          ...lastMsg,
          text,
          isComplete
        };
        return updated;
      }
      return [
        ...prev,
        {
          text,
          sender: "Gemini",
          timestamp: new Date().toLocaleTimeString(),
          isComplete: isComplete,
          type: "text"
        }
      ];
    });
  };

  useEffect(() => {
    if (!lastTranscription) return;
    pendingRef.current += lastTranscription.text;

    if (lastTranscription.finished) {
      commitTranscription(pendingRef.current, true);
      pendingRef.current = "";
      if (debounceRef.current) clearTimeout(debounceRef.current);
    } else {
      if (debounceRef.current) clearTimeout(debounceRef.current);
      debounceRef.current = setTimeout(() => {
        commitTranscription(pendingRef.current, false);
      }, 200);
    }
  }, [lastTranscription]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <Card className="w-full lg:w-1/2">
      <CardHeader>
        <CardTitle>Chat</CardTitle>
      </CardHeader>
      <CardContent>
        <ScrollArea className="pr-2">
          <div className="space-y-4">
            {messages.map((message, index) => (
              message.text.trim() && (
                <div key={index} className="flex items-start space-x-4 rounded-lg p-4 bg-muted/50">
                  {message.sender === "Gemini" && (
                    <Avatar>
                      <AvatarImage src="/placeholder-avatar.jpg" />
                    </Avatar>
                  )}
                  <div className={`p-3 rounded-lg max-w-[70%] ${
                    message.sender === "Gemini"
                      ? "bg-primary text-primary-foreground"
                      : "bg-secondary text-secondary-foreground"
                  }`}>
                    <p>{message.text}</p>
                    <p className="text-xs text-muted-foreground">
                      {message.isComplete ? message.timestamp : "(typing...)"}
                    </p>
                  </div>
                  {message.sender === "User" && (
                    <Avatar>
                      <AvatarImage src="/user-avatar.jpg" />
                    </Avatar>
                  )}
                </div>
              )
            ))}
            <div ref={chatEndRef} />
          </div>
        </ScrollArea>
      </CardContent>
      <div className="p-4 border-t flex space-x-2">
        <Input
          value={inputText}
          onChange={handleInputChange}
          onKeyPress={e => e.key === "Enter" && handleSendMessage()}
          placeholder="Type a message..."
        />
        <Button onClick={handleSendMessage}>Send</Button>
      </div>
    </Card>
  );
};

export default Chat;