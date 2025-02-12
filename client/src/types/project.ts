export interface ProjectInfo {
    project_name: string;
    chapters: Array<{
        id: string;
        spans: Array<{
            id: string;
            has_content: boolean;
            has_prompt: boolean;
            images: string[];
            audios: string[];
        }>;
    }>;
    knowledge_graph: {
        nodes: any[];
        relationships: any[];
        created_at: string;
    };
}
