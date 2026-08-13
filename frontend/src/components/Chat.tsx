import {
  useEffect,
  useRef,
  useState,
  type KeyboardEvent,
} from "react";


type Message = {
  id: string;
  role: "user" | "assistant";
  text: string;
};


type AITask = {
  title: string;
  note?: string | null;
};


type ChatApiResponse = {
  answer: string;
  tasks: AITask[];
};


type ChatProps = {
  onTasksCreated?: () => void;
};


function generateId() {
  return `${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

export default function Chat({
  onTasksCreated,
}: ChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      text: "Hi! I'm your assistant. Ask me anything or ask me to create a task plan.",
    },
  ]);

  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [suggestedTasks, setSuggestedTasks] = useState<AITask[]>([]);

  const scrollRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);


  useEffect(() => {
    const element = scrollRef.current;

    if (element) {
      element.scrollTop = element.scrollHeight;
    }
  }, [messages, isSending, suggestedTasks]);


  async function sendMessage() {
  console.log("=== sendMessage called ===");

  const text = input.trim();
  console.log("Input:", text);

  if (!text || isSending) {
    console.log("Request cancelled");
    return;
  }

  const userMessage: Message = {
    id: generateId(),
    role: "user",
    text,
  };

  setMessages((previous) => [
    ...previous,
    userMessage,
  ]);

  setInput("");
  setSuggestedTasks([]);
  setIsSending(true);

  try {
    console.log("Before fetch");

    const response = await fetch("/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: text,
      }),
    });

    console.log("After fetch");
    console.log("Status:", response.status);

    if (!response.ok) {
      throw new Error(
        `Request failed: ${response.status}`
      );
    }

    const data =
      (await response.json()) as ChatApiResponse;

    console.log("Response:", data);

    setMessages((previous) => [
      ...previous,
      {
        id: generateId(),
        role: "assistant",
        text: data.answer,
      },
    ]);

    setSuggestedTasks(data.tasks ?? []);
  } catch (error) {
    console.error("Chat error:", error);

    setMessages((previous) => [
      ...previous,
      {
        id: generateId(),
        role: "assistant",
        text: "Sorry, something went wrong.",
      },
    ]);
  } finally {
    console.log("Finished");
    setIsSending(false);
  }
}


  async function createSuggestedTasks() {
    if (
      suggestedTasks.length === 0 ||
      isCreating
    ) {
      return;
    }

    setIsCreating(true);

    try {
      const response = await fetch("/tasks/bulk", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          tasks: suggestedTasks.map((task) => ({
            title: task.title,
            note: task.note ?? null,
            completed: false,
          })),
        }),
      });

      if (!response.ok) {
        throw new Error(
          `Task creation failed: ${response.status}`
        );
      }

      setMessages((previous) => [
        ...previous,
        {
          id: generateId(),
          role: "assistant",
          text: `${suggestedTasks.length} tasks created successfully.`,
        },
      ]);

      setSuggestedTasks([]);

      onTasksCreated?.();
    } catch (error) {
      console.error(error);

      setMessages((previous) => [
        ...previous,
        {
          id: generateId(),
          role: "assistant",
          text: "I couldn't create the tasks. Please try again.",
        },
      ]);
    } finally {
      setIsCreating(false);
    }
  }


  function onKeyDown(
    event: KeyboardEvent<HTMLTextAreaElement>,
  ) {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();
      sendMessage();
    }
  }


  return (
    <div className="flex min-h-[600px] flex-col bg-background text-foreground">

      <header className="border-b border-border px-4 py-3">
        <h2 className="font-semibold">
          AI Assistant
        </h2>

        <p className="text-xs text-muted-foreground">
          Ask anything or generate Todo tasks
        </p>
      </header>


      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto px-4 py-6"
      >
        <div className="mx-auto flex max-w-2xl flex-col gap-4">

          {messages.map((message) => (
            <MessageBubble
              key={message.id}
              message={message}
            />
          ))}


          {isSending && (
            <ThinkingBubble />
          )}


          {suggestedTasks.length > 0 && (
            <div className="rounded-2xl border border-border bg-card p-4">

              <h3 className="font-medium">
                Suggested tasks
              </h3>

              <div className="mt-3 space-y-2">

                {suggestedTasks.map(
                  (task, index) => (
                    <div
                      key={`${task.title}-${index}`}
                      className="rounded-xl bg-muted p-3"
                    >
                      <p className="font-medium">
                        {task.title}
                      </p>

                      {task.note && (
                        <p className="mt-1 text-sm text-muted-foreground">
                          {task.note}
                        </p>
                      )}
                    </div>
                  ),
                )}

              </div>


              <button
                type="button"
                onClick={createSuggestedTasks}
                disabled={isCreating}
                className="mt-4 w-full rounded-xl bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground disabled:opacity-50"
              >
                {isCreating
                  ? "Creating..."
                  : `Create ${suggestedTasks.length} tasks`}
              </button>

            </div>
          )}

        </div>
      </div>


      <div className="border-t border-border p-4">

        <div className="flex gap-2">

          <textarea
            ref={textareaRef}
            value={input}
            onChange={(event) =>
              setInput(event.target.value)
            }
            onKeyDown={onKeyDown}
            rows={1}
            placeholder="Ask AI..."
            className="w-full rounded-xl border border-border bg-background px-3 py-2"
          />

          <button
            type="button"
            onClick={sendMessage}
            disabled={
              isSending ||
              input.trim().length === 0
            }
            className="rounded-xl bg-primary px-4 py-2 text-primary-foreground disabled:opacity-50"
          >
            Send
          </button>

        </div>

      </div>
    </div>
  );
}


function MessageBubble({
  message,
}: {
  message: Message;
}) {
  const isUser =
    message.role === "user";

  return (
    <div
      className={`flex ${
        isUser
          ? "justify-end"
          : "justify-start"
      }`}
    >
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-2 text-sm ${
          isUser
            ? "bg-primary text-primary-foreground"
            : "bg-muted"
        }`}
      >
        {message.text}
      </div>
    </div>
  );
}


function ThinkingBubble() {
  return (
    <div className="text-sm text-muted-foreground">
      Thinking...
    </div>
  );
}