### Full Critical Exercises List with Detailed Requirements
Below is the complete list of 19 critical exercises, combining the original 12 with the additional 7. I've grouped them by category for clarity. For each exercise, I've added a new field: *Detailed Requirements*. This expands on the original *Description* by incorporating key implementation steps, best practices, data structures, algorithms, and edge cases from standard references (e.g., LeetCode, GeeksforGeeks, Medium articles, and official docs). This should give you a clearer roadmap for what to build, including APIs, constraints, and considerations for scalability/ML integration.

Focus on Python implementations with job-relevant tools (e.g., PyTorch, FastAPI, LangChain). Practice sketching first, then coding.

### System Design for ML Systems
1. **Architect a real-time fraud detection system for financial transactions with anomaly detection models. (Initial)**
   - *Description*: Design real-time data streams, model deployment; code with Kafka/PyTorch for inference.
   - *Detailed Requirements*: Ingest transaction data via streams (e.g., Kafka); preprocess features (e.g., amount, location); train/use anomaly models like Isolation Forest or autoencoders in PyTorch; deploy for low-latency inference (<100ms); integrate alerting (e.g., via email/Slack); handle imbalanced data with SMOTE; monitor for drift; test with simulated fraud scenarios, out-of-order timestamps, and high throughput (>1000 TPS).
   - *What you'll learn*: Real-time ML integration, anomaly handling.
   - *Why important for job*: Matches real-time processing and scalable AI for workflows.
   - *Priority*: Critical.

2. **Design an end-to-end sentiment analysis pipeline for customer reviews using LLMs. (Initial)**
   - *Description*: Build pipeline from data prep to API serving; use Hugging Face Transformers.
   - *Detailed Requirements*: Collect/preprocess reviews (tokenization, cleaning); fine-tune LLM (e.g., BERT via Hugging Face) for sentiment (positive/negative/neutral); evaluate with metrics (accuracy, F1); deploy as API endpoint; automate with Airflow/Dagster; handle multilingual text, sarcasm, and batch processing; integrate monitoring for model performance.
   - *What you'll learn*: LLM workflows, end-to-end ownership.
   - *Why important for job*: Directly ties to LLM-powered apps and integration.
   - *Priority*: Critical.

3. **Design a distributed recommendation system for Netflix-like video streaming, including offline batch processing and real-time updates with A/B testing at scale. (Harder)**
   - *Description*: Architect with distributed systems (e.g., Spark), A/B frameworks; simulate in code.
   - *Detailed Requirements*: Use collaborative filtering (e.g., matrix factorization in Spark MLlib); process offline batches for model training; handle real-time updates via streams (Kafka); implement A/B testing (split users, track metrics like CTR); distribute across nodes for scalability; address cold starts, data sparsity; evaluate with offline metrics (NDCG) and online A/B results.
   - *What you'll learn*: Scalability, batch/real-time hybrid, experimentation.
   - *Why important for job*: Emphasizes scalable ML architecture and optimization.
   - *Priority*: Critical.

4. **Design an LLM-based conversational AI for customer support, with context retention, hallucination mitigation, and integration with external knowledge bases. (Harder)**
   - *Description*: Build using LangChain; include RAG for knowledge.
   - *Detailed Requirements*: Use LangChain for chaining prompts; implement RAG with vector DB (e.g., FAISS/Pinecone) for retrieving docs; retain context via memory buffers; mitigate hallucinations with grounding/verification prompts; handle multi-turn dialogs; integrate APIs for actions (e.g., ticket creation); test for coherence, accuracy, and edge cases like ambiguous queries or long contexts.
   - *What you'll learn*: Advanced LLM techniques, context management.
   - *Why important for job*: Core to building LLM apps, as per job's LangChain focus.
   - *Priority*: Critical.

### Object-Oriented Design (OOD) Problems
5. **Create classes for an advanced ML model registry with distributed storage, automated drift detection, and rollback features. (Harder)**
   - *Description*: Extend basic registry with drift monitoring; use libraries like MLflow.
   - *Detailed Requirements*: Design classes for model storage (e.g., S3-compatible); implement versioning with metadata (params, metrics); add drift detection (e.g., KS-test on features/predictions); automate rollback via triggers; integrate with distributed storage (e.g., MinIO); ensure thread-safety; test with sample models, simulated drift, and high-volume registrations.
   - *What you'll learn*: Advanced monitoring, distribution.
   - *Why important for job*: Critical for ML lifecycle in DevOps.
   - *Priority*: Critical.

### API or Microservice Design
6. **Build a microservice for image classification predictions from a pre-trained model. (Initial)**
   - *Description*: Create FastAPI service; deploy model with PyTorch.
   - *Detailed Requirements*: Load pre-trained model (e.g., ResNet from PyTorch Hub); expose POST endpoint for image upload (multipart/form-data); preprocess images (resize, normalize); perform inference; return class probabilities; add error handling (invalid images); dockerize for deployment; optimize for GPU if available; test with batch requests and malformed inputs.
   - *What you'll learn*: Microservice basics, ML inference.
   - *Why important for job*: Directly matches building scalable APIs for AI.
   - *Priority*: Critical.

7. **Build an async API for large-scale image processing, using queues for batch inference with distributed ML workers. (Harder)**
   - *Description*: Use Celery/RabbitMQ for queues; scale inference.
   - *Detailed Requirements*: Build FastAPI async endpoints; enqueue tasks to Celery with RabbitMQ broker; distribute workers across nodes for parallel inference (e.g., PyTorch models); handle batching for efficiency; monitor queue lengths; implement retries for failures; scale horizontally; test with high-volume uploads, worker failures, and varying batch sizes.
   - *What you'll learn*: Async design, distributed processing.
   - *Why important for job*: Supports scalable, real-time AI delivery.
   - *Priority*: Critical.

8. **Design a recommendation microservice with gRPC for low-latency calls, integrating real-time user data streams. (Harder)**
   - *Description*: Implement gRPC service with stream integration.
   - *Detailed Requirements*: Define proto files for services (e.g., GetRecommendations); implement server/client in Python; integrate streams (e.g., Kafka for user events); use ML model for recs (e.g., embedding-based); ensure low-latency (<50ms); add authentication (e.g., JWT); handle bidirectional streaming; test with concurrent calls and stream interruptions.
   - *What you'll learn*: Low-latency protocols, streaming.
   - *Why important for job*: Key for performant microservices in SaaS.
   - *Priority*: Critical.

9. **Design an API for ML model lifecycle management, including automated retraining triggers and versioning via GitOps. (Harder)**
   - *Description*: Build API with triggers; integrate Git for versioning.
   - *Detailed Requirements*: Expose REST endpoints (e.g., /register, /retrain); use Git for model versioning (e.g., MLflow + Git); trigger retraining on data drift/events (e.g., via webhooks); automate CI/CD with GitOps (e.g., ArgoCD); track stages (train, validate, deploy); handle rollbacks; test with simulated drifts and pipeline failures.
   - *What you'll learn*: Lifecycle automation, DevOps.
   - *Why important for job*: Matches DevOps and model optimization.
   - *Priority*: Critical.

### ML-Specific Design
10. **Design a script for deploying and monitoring an LLM-based chatbot endpoint. (Initial)**
    - *Description*: Use FastAPI/Docker; add monitoring with Prometheus.
    - *Detailed Requirements*: Build FastAPI app with /chat endpoint; load LLM (e.g., via Hugging Face); dockerize with multi-stage build; deploy to container orch (e.g., Kubernetes); integrate Prometheus for metrics (latency, errors); add logging (e.g., ELK); handle scaling; test with load (e.g., Locust) and failure scenarios.
    - *What you'll learn*: Deployment, monitoring basics.
    - *Why important for job*: Ties to LLM deployment and observability.
    - *Priority*: Critical.

### General Data Structures and Systems
11. **Async Concurrency Limiter (asyncio)**
    - *Description*: Implement with semaphore.
    - *Detailed Requirements*: Define async function to run coroutines with max_concurrency (e.g., Semaphore); use asyncio.gather for parallel execution; preserve order; handle cancellations/timeouts without leaking resources; integrate error propagation; test with varying concurrency levels, failing tasks, and high loads.
    - *What you'll learn*: Async control.
    - *Why important for job*: Handles concurrency in microservices.
    - *Priority*: Critical.

12. **Inverted Index Search (Tiny Engine)**
    - *Description*: Implement indexing/search with ranking.
    - *Detailed Requirements*: Build index with tokenization (e.g., lowercase, stop words removal); use postings lists for docs; support AND/OR queries; rank with TF-IDF; handle phrase queries optionally; manage memory with dicts/lists; test with sample corpus, sparse queries, and growth scenarios.
    - *What you'll learn*: Search engine basics.
    - *Why important for job*: Supports RAG in LLMs.
    - *Priority*: Critical.

13. **LRU Cache**
   - *Description*: Implement get(k), put(k,v) with capacity in O(1) time; use hashmap + custom doubly-linked list.
   - *Detailed Requirements*: Track nodes with prev/next pointers; move to front on access; evict tail on overflow; handle overwrites; no OrderedDict unless allowed; test edges like capacity=1, empty ops, and frequent updates.
   - *What you'll learn*: Efficient caching mechanisms for least recently used eviction.
   - *Why important for job*: Optimizes performance in ML inference serving and microservices by reducing latency through caching.
   - *Priority*: Critical.

14. **Rate-Limited Logger (Per-Message)**
   - *Description*: Implement should_print(timestamp, message) allowing once every 10s per message; use a map for next_allowed_time.
   - *Detailed Requirements*: Use dict to store last print time per message; check/update if timestamp >= next_allowed; handle out-of-order timestamps (sort/assume sorted); support high throughput; test with duplicates, bursts, and varying intervals.
   - *What you'll learn*: Time-based rate limiting per key.
   - *Why important for job*: Protects APIs and microservices from overload, essential for scalable SaaS AI systems.
   - *Priority*: Critical.

15. **Thread-Safe LRU Cache**
   - *Description*: Wrap LRU Cache with concurrency support; use RLock or segmented locks while keeping O(1) operations.
   - *Detailed Requirements*: Extend basic LRU with threading.Lock/RLock; ensure atomic get/put/evict; avoid deadlocks; optional sharding for better concurrency; test under contention, evictions, and stale reads.
   - *What you'll learn*: Concurrent data structure design.
   - *Why important for job*: Enables safe, high-performance caching in multi-threaded ML environments like inference servers.
   - *Priority*: Critical.

16. **Thread Pool (Minimal Executor)**
   - *Description*: Implement submit(fn, *args) -> Future, with worker threads, work queue, and shutdown; handle results and exceptions.
   - *Detailed Requirements*: Use queue.Queue for tasks; spawn fixed threads; Future class for results/exceptions with wait; graceful shutdown with sentinels; handle cancellations; test with exceptions, repeated shutdowns, and varying pool sizes.
   - *What you'll learn*: Parallel task execution and management.
   - *Why important for job*: Supports parallel processing in ML workflows, such as data preprocessing or distributed training.
   - *Priority*: Critical.

17. **Async Token-Bucket Rate Limiter**
   - *Description*: Implement await acquire(n=1) with capacity C and refill r tokens/sec; track tokens and sleep as needed.
   - *Detailed Requirements*: Track current tokens and last_refill; refill based on time delta; await asyncio.sleep if insufficient; support bursts up to C; handle per-key buckets optionally; test with bursts, clock skew, and high-frequency calls.
   - *What you'll learn*: Asynchronous rate limiting with burst control.
   - *Why important for job*: Manages traffic in async microservices and APIs for AI features, preventing bottlenecks.
   - *Priority*: Critical.

18. **Consistent Hash Ring (Sharding)**
   - *Description*: Implement add_node(id), remove_node(id), get_node(key); use virtual nodes on a hash circle with bisect.
   - *Detailed Requirements*: Use sorted list for ring; hash keys/nodes (e.g., hashlib); add multiple vnodes per node for balance; minimize remaps on churn; handle collisions; test with node additions/removals, uneven loads, and large key spaces.
   - *What you'll learn*: Distributed key partitioning with minimal remapping.
   - *Why important for job*: Essential for sharding data in scalable ML systems, like distributed model serving or storage.
   - *Priority*: Critical.

19. **News Feed (“Tiny Twitter”)**
   - *Description*: Implement post(user, tweet), follow(a,b), unfollow(a,b), get_feed(user, k); use per-user posts and heap-merge for feeds.
   - *Detailed Requirements*: Store posts timestamped per user; use graphs for follows; merge feeds with min-heap for top-k; optional push/pull models; handle self-follows, deletes; scale with fan-out limits; test with high fan-in/out and real-time updates.
   - *What you'll learn*: Feed aggregation and social graph handling.
   - *Why important for job*: Mirrors designing personalized recommendation systems, aligning with ML-driven features in B2B SaaS.
   - *Priority*: Critical.