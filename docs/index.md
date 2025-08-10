# Mangolo Framework Documentation

Welcome to the Mangolo Framework documentation. This guide provides comprehensive information about the language syntax, configuration options, and best practices for building applications with Mangolo.

## Core Components

Mangolo uses three primary file types for application development:

1. **`.slice` files** - Data schema definitions
2. **`.knife` files** - API endpoints and business logic
3. **`.mango` files** - Project configuration

## Quick Start

To start a new Mangolo project:

1. Create a project directory
2. Add a `namespace.mango` configuration file
3. Define your data models in `.slice` files
4. Implement your API endpoints in `.knife` files
5. Run your application with the Mangolo CLI

## Documentation Sections

### Schema Definition (.slice)

[Slice Syntax Documentation](slice_syntax.md)

Define your data models with validation rules, relationships, indexes, and access controls.

```
[object]
name: string required min(3) max(50)
email: string required email unique
role: enum("user", "admin") default("user")
```

### API Implementation (.knife)

[Knife Syntax Documentation](knife_syntax.md)

Create HTTP route handlers with middleware, error handling, and business logic.

```
on GET users/:id => authenticate (request) {
    userId = request.params.id
    user = db.users.findOne({ _id: userId })
    
    if !user {
        respond 404 "User not found"
    }
    
    return user
}
```

### Project Configuration (.mango)

[Mango Configuration Reference](mango_configuration.md)

Configure your application with TOML-based settings files.

```toml
[project]
name = "my-app"
version = "1.0.0"

[server]
port = 8080

[database]
type = "postgres"
```

## Best Practices

- Define schemas first, then implement API endpoints
- Use middleware for cross-cutting concerns
- Follow RESTful API design principles
- Implement proper validation and error handling
- Use environment variables for sensitive configuration

## Architecture

Mangolo follows a modular architecture:

1. **Schema Layer** - Data definitions and validation
2. **API Layer** - Route handlers and business logic
3. **Storage Layer** - Database operations and persistence
4. **Service Layer** - External integrations and background tasks

## Contributing

We welcome contributions to the Mangolo framework. Please follow our contribution guidelines when submitting pull requests.

## License

Mangolo is licensed under the MIT License.