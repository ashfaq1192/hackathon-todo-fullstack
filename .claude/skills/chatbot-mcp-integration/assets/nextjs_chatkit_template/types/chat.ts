export interface ChatMessage {
    role: 'user' | 'assistant';
    content: string;
    timestamp: string; // ISO 8601 string
}

export interface Conversation {
    id: string;
    userId: string;
    messages: ChatMessage[];
    createdAt: string;
    updatedAt: string;
}
