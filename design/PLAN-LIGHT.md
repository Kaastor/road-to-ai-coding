#### System Design for ML Systems
1. **Design a basic real-time anomaly detection system for transaction monitoring.**
   - *Description*: Outline data flow and model inference; sketch with PyTorch.
   - *Detailed Requirements*: Diagram ingestion (e.g., simple queue); preprocess features (e.g., normalize amount); use a pre-trained Isolation Forest or basic PyTorch autoencoder; discuss low-latency inference (<200ms) and alerting; consider imbalanced data and drift; simulate with 10-20 sample transactions.
   - *What you'll learn*: Real-time ML basics.
   - *Why important for job*: Aligns with scalable AI workflows.
   - *Priority*: High.

2. **Outline a sentiment analysis pipeline using a pre-trained LLM.**
   - *Description*: Sketch from data to output; use Hugging Face.
   - *Detailed Requirements*: List steps: clean text, fine-tune/infer with BERT (pseudocode); evaluate with F1 score on 50 samples; discuss API deployment and multilingual handling; ignore full training.
   - *What you'll learn*: LLM pipeline essentials.
   - *Why important for job*: Ties to LLM-powered features.
   - *Priority*: High.

3. **Sketch a simple recommendation system with batch processing.**
   - *Description*: Focus on core logic; use basic matrix factorization.
   - *Detailed Requirements*: Diagram user-item matrix; pseudocode collaborative filtering; discuss cold starts and A/B testing basics; simulate on a 100x100 matrix; omit distribution.
   - *What you'll learn*: Recommendation fundamentals.
   - *Why important for job*: Supports scalable ML.
   - *Priority*: Medium.

4. **Design a basic LLM chatbot with context retention.**
   - *Description*: Use LangChain for simple interactions.
   - *Detailed Requirements*: Sketch prompt chaining and memory buffer; integrate RAG with a small vector store (e.g., in-memory dict); discuss hallucination mitigation via prompts; test with 5-10 dialog turns.
   - *What you'll learn*: LLM context handling.
   - *Why important for job*: Core to LangChain-based apps.
   - *Priority*: High.

#### Object-Oriented Design (OOD) Problems
5. **Design classes for a simple ML model registry with versioning.**
   - *Description*: Focus on core classes; mention MLflow concepts.
   - *Detailed Requirements*: Define Model and Registry classes; include methods for register/version; discuss drift detection basics (e.g., simple metric check); pseudocode storage (dict-based); test with 3-5 models.
   - *What you'll learn*: OOD for ML tools.
   - *Why important for job*: Aids ML lifecycle management.
   - *Priority*: Medium.

#### API or Microservice Design
6. **Build a basic FastAPI for image classification inference.**
   - *Description*: Create a simple endpoint; use pre-trained PyTorch model.
   - *Detailed Requirements*: Pseudocode POST route for image upload; preprocess (resize); infer and return class; add basic error handling; discuss Docker basics; test with 2-3 images.
   - *What you'll learn*: API for ML serving.
   - *Why important for job*: Matches AI microservices.
   - *Priority*: High.

7. **Outline an async API for image processing with queuing.**
   - *Description*: Use basic async patterns; mention Celery.
   - *Detailed Requirements*: Sketch FastAPI async endpoint; enqueue to a list/queue; discuss worker scaling; pseudocode inference; test with 5-10 tasks.
   - *What you'll learn*: Async basics.
   - *Why important for job*: Enables scalable AI delivery.
   - *Priority*: Medium.

#### ML-Specific Design
8. **Sketch deployment for an LLM chatbot endpoint.**
   - *Description*: Focus on basics; use FastAPI.
   - *Detailed Requirements*: Diagram /chat route; load LLM pseudocode; discuss monitoring (e.g., log latency); mention Docker; test with 5 queries.
   - *What you'll learn*: Deployment essentials.
   - *Why important for job*: Relates to LLM observability.
   - *Priority*: High.

#### General Data Structures and Systems
9. **Implement a basic LRU Cache.**
   - *Description*: Focus on O(1) operations; use dict and list.
   - *Detailed Requirements*: Code get/put with capacity; handle evictions; test with 10 operations; discuss thread-safety briefly.
   - *What you'll learn*: Caching mechanics.
   - *Why important for job*: Optimizes ML inference.
   - *Priority*: High.

10. **Design a simple rate limiter for messages.**
    - *Description*: Use a dict for timestamps.
    - *Detailed Requirements*: Code should_print; allow once per 10s per message; test with 20 calls; discuss bursts.
    - *What you'll learn*: Rate limiting.
    - *Why important for job*: Protects APIs in SaaS.
    - *Priority*: Medium.