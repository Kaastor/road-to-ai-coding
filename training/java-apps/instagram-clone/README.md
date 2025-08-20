# Instagram Clone - Modular Implementation Plan

## Project Architecture
Transform the current Hello World Java app into an Instagram clone backend with CLI interface, following 5-minute iteration cycles.

## Phase 1: Foundation & User Management (5-6 iterations)

### 1.1: Domain Models & Project Structure (~5 min)
- Create `com.example.instagram` package structure
- Implement `User` record with basic fields (id, username, email, password)
- Add UserTest with basic validation tests
- Update pom.xml artifactId to "instagram-clone"

### 1.2: User Repository Layer (~5 min)  
- Create `UserRepository` interface with CRUD operations
- Implement `InMemoryUserRepository` with Map storage
- Add UserRepositoryTest with save/find operations
- Test storage and retrieval functionality

### 1.3: User Service Layer (~5 min)
- Create `UserService` class with registration logic
- Implement password validation and duplicate username checks
- Add UserServiceTest covering registration scenarios
- Test business logic isolation

### 1.4: Authentication System (~5 min)
- Create `AuthenticationService` for login/logout
- Implement simple session management with Map storage
- Add AuthenticationServiceTest for login flows
- Test credential validation

### 1.5: CLI User Interface (~5 min)
- Create `InstagramCli` main class replacing Hello.java
- Implement user registration and login commands
- Add basic menu system for user interactions
- Manual test: register user, login, view profile

### 1.6: Integration Testing (~5 min)
- Create `UserIntegrationTest` testing full user flow
- Test registration ’ login ’ profile view sequence
- Verify data persistence within session
- Ensure all user stories for authentication work

## Phase 2: Basic Post Management (4-5 iterations)

### 2.1: Post Domain Model (~5 min)
- Create `Post` record (id, userId, content, timestamp)
- Add PostTest for validation and creation
- Implement post creation logic
- Test post data structure

### 2.2: Post Repository (~5 min)
- Create `PostRepository` interface and `InMemoryPostRepository`
- Implement findByUserId, save, findAll methods
- Add PostRepositoryTest for CRUD operations
- Test post storage and user association

### 2.3: Post Service (~5 min)
- Create `PostService` with createPost, getUserPosts methods
- Add content validation and user existence checks
- Add PostServiceTest covering creation scenarios
- Test business rules for post creation

### 2.4: CLI Post Features (~5 min)
- Extend InstagramCli with post creation and viewing
- Add "create post" and "view my posts" commands
- Implement post listing with timestamps
- Manual test: create posts, view user posts

### 2.5: Post Integration Testing (~5 min)
- Add post functionality to integration tests
- Test: login ’ create post ’ view posts sequence
- Verify post-user relationships
- Ensure post user stories work end-to-end

## Phase 3: Image Handling & Storage (3-4 iterations)

### 3.1: Image Storage Foundation (~5 min)
- Update Post model to include optional imagePath field
- Create `ImageService` interface for future implementations
- Implement `FileSystemImageService` for local storage
- Add ImageServiceTest with mock file operations

### 3.2: Image Upload Simulation (~5 min)
- Create CLI command to "upload" images (copy to uploads/ directory)
- Implement image path storage in posts
- Add validation for image file extensions
- Test image association with posts

### 3.3: Image Display in CLI (~5 min)
- Add image path display in post listings
- Implement "view image details" command
- Show image metadata (size, path) in CLI
- Test image information display

### 3.4: Image Integration Testing (~5 min)
- Test complete flow: create post with image ’ view posts with images
- Verify image path storage and retrieval
- Test error handling for missing images
- Ensure image user stories work

## Phase 4: Social Features (4-5 iterations)

### 4.1: Following Domain Model (~5 min)
- Create `Follow` record (followerId, followingId, timestamp)
- Add FollowRepository interface and InMemoryFollowRepository
- Implement follow/unfollow operations
- Add FollowRepositoryTest for relationship storage

### 4.2: Follow Service Layer (~5 min)
- Create `FollowService` with follow/unfollow/isFollowing methods
- Add validation to prevent self-following
- Implement getFollowers and getFollowing methods
- Add FollowServiceTest covering social scenarios

### 4.3: CLI Social Features (~5 min)
- Add "follow user", "unfollow user", "my followers", "my following" commands
- Implement user search functionality
- Add follow/unfollow actions to CLI menu
- Test social interactions manually

### 4.4: User Profile Enhancement (~5 min)
- Update profile view to show follower/following counts
- Add "view user profile" command for other users
- Display user's posts and social stats
- Test enhanced profile functionality

### 4.5: Social Integration Testing (~5 min)
- Test full social flow: follow user ’ view their profile ’ see posts
- Verify follower/following relationships
- Test unfollow functionality
- Ensure all social user stories work

## Phase 5: Feed Generation & Advanced Features (3-4 iterations)

### 5.1: Feed Service (~5 min)
- Create `FeedService` to generate personalized feeds
- Implement getHomeFeed method showing posts from followed users
- Add chronological ordering of posts
- Add FeedServiceTest for feed generation logic

### 5.2: CLI Feed Interface (~5 min)
- Add "view feed" command to CLI
- Display posts from followed users in chronological order
- Show post author, content, and timestamp
- Test feed display with multiple users and posts

### 5.3: Enhanced Feed Features (~5 min)
- Add pagination support for large feeds
- Implement "view user posts" for any user
- Add post count and activity indicators
- Test feed performance with multiple users

### 5.4: Final Integration & Polish (~5 min)
- Comprehensive integration test covering all user stories
- Test complete user journey: register ’ follow ’ post ’ view feed
- Verify all 5 user stories from CLAUDE.md are working
- Final manual testing and bug fixes

## Key Benefits of This Plan:
- **Verifiable**: Each step has concrete deliverables and tests
- **Incremental**: Each iteration builds working functionality
- **Modular**: Clean separation of concerns (domain, repository, service, CLI)
- **Testable**: Unit and integration tests at each layer
- **5-minute cycles**: Each step designed to be completed in ~5 minutes
- **User story driven**: Each phase advances toward complete user stories

## Technical Foundation:
- Java 17 with Maven
- In-memory storage (easily replaceable with database later)
- CLI interface (can be extended to REST API + web frontend)
- JUnit 5 testing throughout
- SLF4J logging for production readiness

## User Stories Mapping:
1. **User registration/login** ’ Phase 1 (iterations 1.1-1.6)
2. **Create posts with images** ’ Phase 2 + 3 (iterations 2.1-3.4)
3. **User profile with uploaded images** ’ Phase 2 (iterations 2.1-2.5)
4. **Follow other users** ’ Phase 4 (iterations 4.1-4.5)
5. **See posts from followed users** ’ Phase 5 (iterations 5.1-5.4)