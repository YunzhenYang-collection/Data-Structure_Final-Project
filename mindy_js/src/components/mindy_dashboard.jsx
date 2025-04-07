
/*
import React, { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export default function MindyDashboard() {
  const [summary, setSummary] = useState({});
  const [reminders, setReminders] = useState([]);
  const [interviewQuestions, setInterviewQuestions] = useState([]);
  const [studyProgress, setStudyProgress] = useState([]);
  const [savings, setSavings] = useState({ goal: 0, saved: 0 });

  useEffect(() => {
    fetch("http://127.0.0.1:5000/api/summary").then(res => res.json()).then(setSummary);
    fetch("http://127.0.0.1:5000/api/reminders").then(res => res.json()).then(setReminders);
    fetch("http://127.0.0.1:5000/api/interview").then(res => res.json()).then(setInterviewQuestions);
    fetch("http://127.0.0.1:5000/api/study").then(res => res.json()).then(setStudyProgress);
    fetch("http://127.0.0.1:5000/api/savings").then(res => res.json()).then(setSavings);
  }, []);

  const addSavings = (amount) => {
    fetch("http://127.0.0.1:5000/api/savings/add", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ amount })
    })
      .then(res => res.json())
      .then(setSavings);
  };

  return (
    <div className="p-4 space-y-6">
      <h1 className="text-3xl font-bold">MINDY Dashboard</h1>
      <Tabs defaultValue="summary" className="space-y-4">
        <TabsList>
          <TabsTrigger value="summary">Daily Summary</TabsTrigger>
          <TabsTrigger value="reminder">Reminders</TabsTrigger>
          <TabsTrigger value="interview">Interview Coach</TabsTrigger>
          <TabsTrigger value="student">Study Tracker</TabsTrigger>
          <TabsTrigger value="savings">Saving Jar</TabsTrigger>
        </TabsList>

        <TabsContent value="summary">
          <Card>
            <CardContent className="space-y-2 pt-4">
              <h2 className="text-xl font-semibold">Today's Digest</h2>
              <p><strong>Headline:</strong> {summary.headline}</p>
              <p><strong>Summary:</strong> {summary.summary}</p>
              <p><strong>Suggestion:</strong> {summary.suggestion}</p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="reminder">
          <Card>
            <CardContent className="space-y-4 pt-4">
              <h2 className="text-xl font-semibold">Today's Reminders</h2>
              <ul className="list-disc pl-6 space-y-1">
                {reminders.map((r, i) => (
                  <li key={i}>{r.done ? "✅" : "⬜"} {r.task}</li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="interview">
          <Card>
            <CardContent className="space-y-4 pt-4">
              <h2 className="text-xl font-semibold">Mock Interview</h2>
              <ul className="list-disc pl-6 space-y-1">
                {interviewQuestions.map((q, i) => (
                  <li key={i}>{q}</li>
                ))}
              </ul>
              <Textarea placeholder="Your response..." />
              <Button>Submit</Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="student">
          <Card>
            <CardContent className="space-y-4 pt-4">
              <h2 className="text-xl font-semibold">Study Progress</h2>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={studyProgress}>
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="Progress" fill="#4f46e5" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="savings">
          <Card>
            <CardContent className="space-y-4 pt-4">
              <h2 className="text-xl font-semibold">Saving Jar</h2>
              <p>Goal: ${savings.goal} | Saved: ${savings.saved}</p>
              <Progress value={(savings.saved / savings.goal) * 100} />
              <Button onClick={() => addSavings(100)}>+ Add $100</Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
*/
// mock模擬版本(非正式版)
import React, { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export default function MindyDashboard() {
  const [summary, setSummary] = useState({});
  const [reminders, setReminders] = useState([]);
  const [interviewQuestions, setInterviewQuestions] = useState([]);
  const [studyProgress, setStudyProgress] = useState([]);
  const [savings, setSavings] = useState({ goal: 0, saved: 0 });

  // 用 mock data 模擬後端
  useEffect(() => {
    setSummary({
      headline: "AI dominates 2025 market",
      summary: "Artificial Intelligence continues to revolutionize industries.",
      suggestion: "Learn more about machine learning and data ethics."
    });
    setReminders([
      { task: "Finish report", done: false },
      { task: "Team meeting at 3PM", done: true }
    ]);
    setInterviewQuestions([
      "Tell me about yourself.",
      "What is your biggest strength?",
      "Explain a project you are proud of."
    ]);
    setStudyProgress([
      { name: "Math", Progress: 80 },
      { name: "English", Progress: 65 },
      { name: "CS", Progress: 90 }
    ]);
    setSavings({ goal: 1000, saved: 400 });
  }, []);

  const addSavings = (amount) => {
    setSavings(prev => {
      const newSaved = prev.saved + amount;
      return { ...prev, saved: newSaved > prev.goal ? prev.goal : newSaved };
    });
  };

  return (
    <div className="p-4 space-y-6">
      <h1 className="text-3xl font-bold">MINDY Dashboard</h1>
      <Tabs defaultValue="summary" className="space-y-4">
        <TabsList>
          <TabsTrigger value="summary">Daily Summary</TabsTrigger>
          <TabsTrigger value="reminder">Reminders</TabsTrigger>
          <TabsTrigger value="interview">Interview Coach</TabsTrigger>
          <TabsTrigger value="student">Study Tracker</TabsTrigger>
          <TabsTrigger value="savings">Saving Jar</TabsTrigger>
        </TabsList>

        <TabsContent value="summary">
          <Card>
            <CardContent className="space-y-2 pt-4">
              <h2 className="text-xl font-semibold">Today's Digest</h2>
              <p><strong>Headline:</strong> {summary.headline}</p>
              <p><strong>Summary:</strong> {summary.summary}</p>
              <p><strong>Suggestion:</strong> {summary.suggestion}</p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="reminder">
          <Card>
            <CardContent className="space-y-4 pt-4">
              <h2 className="text-xl font-semibold">Today's Reminders</h2>
              <ul className="list-disc pl-6 space-y-1">
                {reminders.map((r, i) => (
                  <li key={i}>{r.done ? "✅" : "⬜"} {r.task}</li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="interview">
          <Card>
            <CardContent className="space-y-4 pt-4">
              <h2 className="text-xl font-semibold">Mock Interview</h2>
              <ul className="list-disc pl-6 space-y-1">
                {interviewQuestions.map((q, i) => (
                  <li key={i}>{q}</li>
                ))}
              </ul>
              <Textarea placeholder="Your response..." />
              <Button>Submit</Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="student">
          <Card>
            <CardContent className="space-y-4 pt-4">
              <h2 className="text-xl font-semibold">Study Progress</h2>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={studyProgress}>
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="Progress" fill="#4f46e5" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="savings">
          <Card>
            <CardContent className="space-y-4 pt-4">
              <h2 className="text-xl font-semibold">Saving Jar</h2>
              <p>Goal: ${savings.goal} | Saved: ${savings.saved}</p>
              <Progress value={(savings.saved / savings.goal) * 100} />
              <Button onClick={() => addSavings(100)}>+ Add $100</Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
