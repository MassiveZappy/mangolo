# Mangolo Knife Syntax Reference

`.knife` files define API endpoints and business logic in the Mangolo framework. They provide a clean, expressive way to handle HTTP requests, process data, and implement routing logic.

## Table of Contents

- [Basic Structure](#basic-structure)
- [Route Handlers](#route-handlers)
- [Functions](#functions)
- [Middleware](#middleware)
- [Error Handling](#error-handling)
- [Request Processing](#request-processing)
- [Response Generation](#response-generation)
- [Control Flow](#control-flow)
- [Examples](#examples)

## Basic Structure

A `.knife` file can contain route handlers, functions, and middleware definitions:

```
// Function definition
def functionName(param1, param2) {
    // function body
    return result
}

// Middleware definition
middleware middlewareName(request, next) {
    // pre-processing
    response = next()
    // post-processing
    return response
}

// Route handler
on METHOD path (request) {
    // request handling logic
    return response
}

// Error handler
catch METHOD path (request, error) {
    // error handling logic
    respond statusCode body
}
```

## Route Handlers

Route handlers define the endpoints of your API and specify how to process incoming HTTP requests.

### Basic Route Syntax

```
on METHOD path (request) {
    // handler body
}
```

Where:
- `METHOD` is an HTTP method: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, etc.
- `path` is the URL path, which can include parameters
- `request` is the incoming request object

### Route Parameters

```
on GET users/:id (request) {
    userId = request.params.id
    // use userId
}
```

### Query Parameters

```
on GET search (request) {
    term = request.query.term
    page = int(request.query.page || 1)
    // use term and page
}
```

### Applying Middleware

```
on GET protected => authenticate, authorize (request) {
    // Only executed if middleware passes
}
```

## Functions

Functions allow you to encapsulate reusable logic.

### Function Definition

```
def calculateTotal(items, taxRate) {
    subtotal = items.sum(item => item.price * item.quantity)
    tax = subtotal * taxRate
    return subtotal + tax
}
```

### Function Invocation

```
total = calculateTotal(cart.items, 0.08)
```

## Middleware

Middleware functions process requests before they reach route handlers or after responses are generated.

### Middleware Definition

```
middleware logRequest(request, next) {
    startTime = now()
    
    // Call next middleware or route handler
    response = next()
    
    // Post-processing
    duration = now() - startTime
    log("${request.method} ${request.path} - ${duration}ms")
    
    return response
}
```

### Middleware with Early Return

```
middleware authenticate(request, next) {
    if !request.headers.authorization {
        respond 401 "Authentication required"
    }
    
    // Continue to next middleware or handler
    return next()
}
```

## Error Handling

Knife provides several mechanisms for error handling.

### Try-Catch Blocks

```
try {
    // code that might throw errors
} catch error {
    // handle error
} finally {
    // always executed
}
```

### Typed Error Catching

```
try {
    // risky code
} catch ValidationError as err {
    // handle validation errors
} catch DatabaseError as err {
    // handle database errors
} catch error {
    // handle other errors
}
```

### Route-Level Error Handlers

```
catch POST users (request, error) {
    logException(error)
    
    if error instanceof ValidationError {
        respond 400 error.message
    } else {
        respond 500 "Internal server error"
    }
}
```

### Global Error Handlers

```
catch ALL /api/* (request, error) {
    // Handles all errors for routes starting with /api/
}
```

## Request Processing

### Request Properties

| Property | Description | Example |
|----------|-------------|---------|
| `request.method` | HTTP method | `"GET"`, `"POST"` |
| `request.path` | Request path | `"/users/123"` |
| `request.params` | Path parameters | `request.params.id` |
| `request.query` | Query parameters | `request.query.sort` |
| `request.headers` | HTTP headers | `request.headers.authorization` |
| `request.body` | Raw request body | `request.body` |
| `request.resource` | Parsed request body | `request.resource.name` |
| `request.ip` | Client IP address | `request.ip` |
| `request.auth` | Authentication context | `request.auth.userId` |

### Data Validation

```
validate request.resource {
    name: required string min(3) max(50),
    email: required email,
    age: optional number min(18)
}
```

### Data Transformation

```
transform request.body {
    parse_json(),
    sanitize("html"),
    remove_fields(["password", "token"])
}
```

## Response Generation

### Simple Responses

```
return {
    message: "Success",
    data: result
}
```

### Explicit Responses

```
respond 200 {
    status: "success",
    data: users
}
```

### Status Code Responses

```
respond 201 "Resource created successfully"
respond 400 "Bad request"
respond 404 "Resource not found"
```

### Response with Headers

```
respond 200 {
    body: data,
    headers: {
        "Content-Type": "application/pdf",
        "Content-Disposition": "attachment; filename=report.pdf"
    }
}
```

### Redirects

```
redirect "/new-location"
redirect 301 "https://example.com"
```

## Control Flow

### Conditionals

```
if condition {
    // true branch
} else if anotherCondition {
    // else if branch
} else {
    // else branch
}
```

### Pattern Matching

```
match value {
    "string" -> doSomething(),
    number if number > 0 -> handlePositive(number),
    { type: "user", id: id } -> processUser(id),
    _ -> handleDefault()
}
```

### Loops

```
for item in collection {
    // process item
}

while condition {
    // loop body
}
```

### Early Returns

```
if !isValid {
    respond 400 "Invalid request"
}

// Continue processing if valid
```

## Database Operations

```
// Find one record
user = db.users.findOne({ _id: userId })

// Query with criteria
activeUsers = db.users.find({ status: "active" })
    .sort({ created_at: -1 })
    .limit(10)

// Create record
newId = db.posts.create({
    title: "New Post",
    content: "Content here"
})

// Update record
db.users.update(userId, {
    last_login: now()
})

// Delete record
db.products.delete(productId)

// Transactions
transaction {
    fromAccount = db.accounts.findOne({ _id: fromId })
    toAccount = db.accounts.findOne({ _id: toId })
    
    db.accounts.update(fromId, { balance: fromAccount.balance - amount })
    db.accounts.update(toId, { balance: toAccount.balance + amount })
    
    db.transfers.create({
        from: fromId,
        to: toId,
        amount: amount,
        timestamp: now()
    })
}
```

## Background Tasks

```
// Queue a task
queue("send_welcome_email", {
    to: user.email,
    username: user.username
})

// Schedule a task
schedule("generate_report", {
    reportId: report.id
}, {
    delay: "30m",
    retry: 3
})
```

## Utilities

```
// Logging
log("Info message")
logWarn("Warning message")
logError("Error message")
logException(error)

// Date/Time
now()
dateAdd(date, "1d")
formatDate(date, "YYYY-MM-DD")

// String operations
"${variable} text"
text.includes(substring)
text.replace(pattern, replacement)

// Type conversion
int(value)
float(value)
string(value)
boolean(value)
```

## Examples

### User Authentication

```
on POST login (request) {
    try {
        validate request.body {
            email: required email,
            password: required string
        }
        
        user = db.users.findOne({ email: request.body.email })
        if !user {
            respond 401 "Invalid email or password"
        }
        
        if !verifyPassword(request.body.password, user.password) {
            // Increment failed attempts
            db.users.update(user._id, {
                failed_login_attempts: (user.failed_login_attempts || 0) + 1,
                last_failed_login: now()
            })
            
            respond 401 "Invalid email or password"
        }
        
        // Reset failed attempts on success
        db.users.update(user._id, {
            failed_login_attempts: 0,
            last_login: now()
        })
        
        // Generate token
        token = generateJWT({
            userId: user._id,
            role: user.role
        })
        
        return {
            token: token,
            user: {
                id: user._id,
                name: user.name,
                email: user.email,
                role: user.role
            }
        }
    } catch error {
        logException(error)
        respond 500 "Authentication failed"
    }
}
```

### CRUD Operations

```
// Create
on POST products (request) {
    validate request.resource {
        name: required string min(3),
        price: required number positive,
        description: optional string
    }
    
    productId = db.products.create(request.resource)
    
    respond 201 {
        message: "Product created",
        productId: productId
    }
}

// Read
on GET products/:id (request) {
    product = db.products.findOne({ _id: request.params.id })
    
    if !product {
        respond 404 "Product not found"
    }
    
    return product
}

// Update
on PUT products/:id (request) {
    if !db.products.exists({ _id: request.params.id }) {
        respond 404 "Product not found"
    }
    
    validate request.resource {
        name: optional string min(3),
        price: optional number positive,
        description: optional string
    }
    
    db.products.update(request.params.id, request.resource)
    
    respond 200 "Product updated successfully"
}

// Delete
on DELETE products/:id (request) {
    if !db.products.exists({ _id: request.params.id }) {
        respond 404 "Product not found"
    }
    
    db.products.delete(request.params.id)
    
    respond 204
}
```

### File Upload

```
on POST upload => authenticate (request) {
    try {
        if !request.files || !request.files.document {
            respond 400 "No file uploaded"
        }
        
        file = request.files.document
        
        // Validate file
        if file.size > 10 * 1024 * 1024 {
            respond 400 "File too large (max 10MB)"
        }
        
        if !["application/pdf", "image/jpeg", "image/png"].includes(file.mimetype) {
            respond 400 "Invalid file type"
        }
        
        // Generate unique filename
        filename = `${uuid()}-${file.name}`
        
        // Save file
        savedPath = saveFile(file, "uploads/" + filename)
        
        // Create file record
        fileId = db.files.create({
            filename: filename,
            original_name: file.name,
            path: savedPath,
            size: file.size,
            mime_type: file.mimetype,
            uploaded_by: request.auth.userId,
            uploaded_at: now()
        })
        
        return {
            id: fileId,
            filename: filename,
            url: `/files/${fileId}`
        }
    } catch error {
        logException(error)
        respond 500 "File upload failed"
    }
}
```

### Advanced Search API

```
on GET search (request) {
    // Parse query parameters with defaults
    let {
        q = "",
        type = "all",
        page = 1,
        limit = 20,
        sort = "relevance",
        order = "desc"
    } = request.query
    
    // Validate and convert params
    page = int(page)
    limit = int(limit)
    
    if page < 1 || limit < 1 || limit > 100 {
        respond 400 "Invalid pagination parameters"
    }
    
    // Build search query
    query = { $text: { $search: q } }
    
    if type != "all" {
        query.type = type
    }
    
    // Execute search with pagination
    results = db.content.find(query)
        .sort({ [sort]: order == "desc" ? -1 : 1 })
        .skip((page - 1) * limit)
        .limit(limit)
        .project({ score: { $meta: "textScore" } })
    
    // Get total for pagination
    total = db.content.count(query)
    
    // Enhance results
    enhanced = results.map(item => {
        return {
            ...item,
            url: `/content/${item._id}`,
            thumbnail: item.image ? `/images/thumbnails/${item.image}` : null
        }
    })
    
    return {
        results: enhanced,
        metadata: {
            total: total,
            page: page,
            limit: limit,
            pages: Math.ceil(total / limit)
        }
    }
}
```
