import { generateText} from "ai";
import OpenAI from "openai";
import dotenv from "dotenv";
dotenv.config();

const client = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
});

async function main() {
    const text = await generateText({
        model: OpenAI("gpt-4o-mini"),
        prompt: "write a short story about a c ronaldo"
    })
}