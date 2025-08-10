# Mangolo Slice Syntax Reference

`.slice` files define data schemas within the Mangolo framework. They provide a declarative way to specify object structures, validation rules, relationships, and access controls.

## Table of Contents

- [Basic Structure](#basic-structure)
- [Field Types](#field-types)
- [Field Modifiers](#field-modifiers)
- [Relationships](#relationships)
- [Sections](#sections)
- [Advanced Features](#advanced-features)
- [Examples](#examples)

## Basic Structure

A `.slice` file consists of multiple sections, with the primary one being `[object]`:

```
[object]
field_name: type modifiers
another_field: another_type more_modifiers
```

## Field Types

| Type | Description | Example |
|------|-------------|---------|
| `string` | Text data | `name: string` |
| `number` | Numeric data | `age: number` |
| `boolean` | True/false value | `active: boolean` |
| `date` | Date value | `birthday: date` |
| `timestamp` | Date and time value | `created_at: timestamp` |
| `enum` | Limited set of values | `status: enum("active", "inactive")` |
| `object` | Nested object | `address: object { street: string, city: string }` |
| `array` | List of values | `tags: array<string>` |
| `file` | File reference | `avatar: file` |
| `relation` | Reference to another object | `author: relation<user>` |

## Field Modifiers

### Common Modifiers

| Modifier | Description | Example |
|----------|-------------|---------|
| `required` | Field must be present | `email: string required` |
| `optional` | Field is optional (default) | `bio: string optional` |
| `default(value)` | Default value if not provided | `role: string default("user")` |
| `unique` | Value must be unique in database | `username: string unique` |
| `encrypted` | Value should be stored encrypted | `ssn: string encrypted` |

### String Modifiers

| Modifier | Description | Example |
|----------|-------------|---------|
| `min(n)` | Minimum length | `password: string min(8)` |
| `max(n)` | Maximum length | `title: string max(100)` |
| `pattern("regex")` | Regular expression validation | `username: string pattern("^[a-z0-9_]+$")` |
| `email` | Must be valid email | `contact: string email` |
| `url` | Must be valid URL | `website: string url` |
| `bcrypt` | Password hashing | `password: string bcrypt` |

### Number Modifiers

| Modifier | Description | Example |
|----------|-------------|---------|
| `min(n)` | Minimum value | `age: number min(18)` |
| `max(n)` | Maximum value | `rating: number max(5)` |
| `between(min, max)` | Value in range | `score: number between(0, 100)` |
| `integer` | Must be an integer | `count: number integer` |
| `positive` | Must be positive | `quantity: number positive` |

### Array Modifiers

| Modifier | Description | Example |
|----------|-------------|---------|
| `min_items(n)` | Minimum items | `tags: array<string> min_items(1)` |
| `max_items(n)` | Maximum items | `images: array<file> max_items(5)` |
| `no_duplicates` | No duplicate items | `categories: array<string> no_duplicates` |
| `max_size(size)` | Maximum total size | `attachments: array<file> max_size(10MB)` |
| `discard_strategy(s)` | Strategy when max reached | `logs: array<string> discard_strategy(oldest)` |

### File Modifiers

| Modifier | Description | Example |
|----------|-------------|---------|
| `max_size(size)` | Maximum file size | `attachment: file max_size(2MB)` |
| `types(list)` | Allowed file types | `image: file types("image/jpeg", "image/png")` |

### Auto Field Modifiers

| Modifier | Description | Example |
|----------|-------------|---------|
| `auto_now` | Set to current time on create | `created_at: timestamp auto_now` |
| `auto_update` | Update to current time on changes | `updated_at: timestamp auto_update` |
| `auto_increment` | Auto incrementing number | `position: number auto_increment` |

## Relationships

### Relation Types

| Type | Description | Example |
|------|-------------|---------|
| `relation<type>` | Basic relation | `author: relation<user>` |
| `foreign_key(field)` | Specify foreign key | `owner: relation<user>(foreign_key("owner_id"))` |
| `many_to_many` | Many-to-many relation | `tags: relation<tag>(many_to_many)` |
| `through(table)` | Junction table | `members: relation<user>(through("memberships"))` |
| `back_reference(field)` | Opposite relation | `children: relation<category>(back_reference("parent"))` |

### Relation Modifiers

| Modifier | Description | Example |
|----------|-------------|---------|
| `required` | Relation must exist | `category: relation<category> required` |
| `on_delete(action)` | Action on parent delete | `author: relation<user>(on_delete("cascade"))` |
| `with_fields(list)` | Extra fields in relation | `members: relation<user>(with_fields(["role", "joined_at"]))` |

## Sections

`.slice` files can contain multiple sections:

### [object]

Defines the fields and their types.

```
[object]
name: string required
email: string required email
```

### [indexes]

Defines database indexes for efficient queries.

```
[indexes]
name_idx: { fields: ["name"], type: "btree" }
email_idx: { fields: ["email"], type: "unique" }
composite_idx: { fields: ["status", "created_at"], type: "btree" }
```

### [permissions]

Defines access control for the object.

```
[permissions]
create: ["admin", "api"]
read: ["public", "user", "admin"]
update: ["self", "admin"]
delete: ["admin"]
```

### [validations]

Defines custom validation rules.

```
[validations]
rule valid_date {
    validate: "end_date > start_date"
    message: "End date must be after start date"
}

rule admin_approval {
    condition: "status == 'published'"
    validate: "approved_by != null"
    message: "Published content requires admin approval"
}
```

## Advanced Features

### Computed Fields

Fields that are calculated from other fields:

```
[object]
first_name: string required
last_name: string required
full_name: computed "${first_name} ${last_name}"
```

### Conditional Fields

Fields that are required only under certain conditions:

```
[object]
type: enum("individual", "company")
company_name: string required(type == "company")
tax_id: string required(type == "company")
```

### Versioned Fields

Fields that track history:

```
[object]
content: string versioned
status: enum("draft", "published") versioned
```

## Examples

### User Schema

```
[object]
username: string required min(3) max(20) pattern("^[a-zA-Z0-9_]+$") unique
email: string required email unique
password: string required min(8) bcrypt
role: enum("user", "admin") default("user")
created_at: timestamp auto_now
profile: object {
    display_name: string optional max(50),
    bio: string optional max(500),
    avatar: file optional max_size(1MB) types("image/jpeg", "image/png")
}

[indexes]
username_idx: { fields: ["username"], type: "btree" }
email_idx: { fields: ["email"], type: "unique" }
role_created_idx: { fields: ["role", "created_at"], type: "btree" }

[permissions]
create: ["admin", "api"]
read: ["self", "admin"]
update: ["self", "admin"]
delete: ["admin"]

[validations]
rule password_strength {
    validate: "password.length >= 8 &&
              password.matches(/[A-Z]/) &&
              password.matches(/[0-9]/) &&
              password.matches(/[^A-Za-z0-9]/)"
    message: "Password must be at least 8 characters and include uppercase, number, and special character"
}
```

### Blog Post Schema

```
[object]
title: string required min(5) max(200)
slug: string required unique pattern("^[a-z0-9-]+$")
content: string required min(50) versioned
status: enum("draft", "published", "archived") default("draft")
author: relation<user> required
tags: array<string> max_items(10) no_duplicates
published_at: timestamp optional
created_at: timestamp auto_now
updated_at: timestamp auto_update

[indexes]
slug_idx: { fields: ["slug"], type: "unique" }
status_date_idx: { fields: ["status", "published_at"], type: "btree" }
author_idx: { fields: ["author"], type: "btree" }

[permissions]
create: ["writer", "admin"]
read: {
    "draft": ["author", "editor", "admin"],
    "published": ["public"],
    "archived": ["author", "admin"]
}
update: ["author", "editor", "admin"]
delete: ["author", "admin"]

[validations]
rule published_requirements {
    condition: "status == 'published'"
    validate: "published_at != null && content.length >= 100"
    message: "Published posts require a publication date and at least 100 characters"
}
```
