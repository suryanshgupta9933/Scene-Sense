# Scene-Sense
Scene Sense is an AI-powered search engine gallery app that revolutionizes the way users interact with their photo collections. 
With Scene Sense, finding the perfect photo becomes a breeze as users can search using natural language queries.

>**Note:** This is a proof of concept and is not intended for production use.

## Inspiration
I was inspired by the idea of using AI to help users find photos in their gallery. I wanted to create a search engine that would allow users to search for photos based on the scene in the photo and be descriptive.

## Brief Working
- Scene Sense uses the CLIP model to understand natural language queries and image content, providing
accurate and contextually relevant results.
- App handles multiple users, a robust user authentication system is implemented using FastAPI. User
credentials are stored in MongoDB and it uses password hashing techniques and JSON Web Token (JWT).
- The app leverages Google Cloud Platform for storage and deployment and Pinecone for embedding
management, enabling efficient and fast image retrieval.

## Old Demo
https://github.com/suryanshgupta9933/Scene-Sense/assets/75354950/11ee5e06-4d73-47d9-9ff6-3ac13334f905