# TypeScript Style Guide: The Elements of Code

## I. Elementary Rules of Usage

### 1. Enable strict mode.
Wrong:
```json
{
  "compilerOptions": {
    "strict": false
  }
}
```
Right:
```json
{
  "compilerOptions": {
    "strict": true
  }
}
```

TypeScript without strict mode is JavaScript with extra steps. Use the full power of the type system.

### 2. Prefer const assertions and readonly.
Wrong:
```typescript
const config = {
  apiUrl: 'https://api.example.com',
  timeout: 5000
};
config.timeout = 10000; // Mutation allowed
```
Right:
```typescript
const config = {
  apiUrl: 'https://api.example.com',
  timeout: 5000
} as const;

// Or for objects that need type annotation:
interface Config {
  readonly apiUrl: string;
  readonly timeout: number;
}
```

Immutability is clarity. Declare your intentions.

### 3. Use unknown over any.
Wrong:
```typescript
function process(data: any) {
  return data.toLowerCase(); // No type checking
}
```
Right:
```typescript
function process(data: unknown) {
  if (typeof data === 'string') {
    return data.toLowerCase();
  }
  throw new Error('Invalid data type');
}
```

`any` disables TypeScript. `unknown` enforces safety.

### 4. Let TypeScript infer when obvious.
Wrong:
```typescript
const name: string = 'William';
const count: number = 42;
const items: string[] = ['a', 'b', 'c'];
```
Right:
```typescript
const name = 'William';
const count = 42;
const items = ['a', 'b', 'c'];
```

Do not state the obvious. TypeScript knows.

## II. Elementary Principles of Composition

### 5. Use interfaces for objects, types for unions and primitives.
Wrong:
```typescript
type User = {
  name: string;
  email: string;
};

interface Status = 'active' | 'inactive';
```
Right:
```typescript
interface User {
  name: string;
  email: string;
}

type Status = 'active' | 'inactive';
type ID = string | number;
```

Interfaces are for shapes. Types are for aliases and unions.

### 6. Make illegal states unrepresentable.
Wrong:
```typescript
interface State {
  isLoading: boolean;
  error?: Error;
  data?: string;
}
// Can be loading with error, or have data with error
```
Right:
```typescript
type State = 
  | { status: 'loading' }
  | { status: 'error'; error: Error }
  | { status: 'success'; data: string };
```

The type system is your first unit test.

### 7. Use discriminated unions over optional properties.
Wrong:
```typescript
interface Response {
  success: boolean;
  data?: string;
  error?: string;
}
```
Right:
```typescript
type Response = 
  | { success: true; data: string }
  | { success: false; error: string };
```

Make the compiler work for you. Exhaustive checking prevents errors.

### 8. Extract types from implementations.
Wrong:
```typescript
interface UserProps {
  name: string;
  age: number;
}

const defaultUser = {
  name: 'Anonymous',
  age: 0
};
```
Right:
```typescript
const defaultUser = {
  name: 'Anonymous',
  age: 0
} as const;

type UserProps = typeof defaultUser;
```

Single source of truth. Let the implementation drive the type.

## III. A Few Matters of Form

### 9. Order type parameters from most to least constrained.
Wrong:
```typescript
function transform<T, K extends keyof T>(obj: T, key: K): T[K]
```
Right:
```typescript
function transform<K extends PropertyKey, T extends Record<K, any>>(
  obj: T, 
  key: K
): T[K]
```

Constraints flow naturally from specific to general.

### 10. Use template literal types for string patterns.
Wrong:
```typescript
type EventName = string;
```
Right:
```typescript
type EventName = `on${Capitalize<string>}`;
// Enforces: 'onClick', 'onChange', etc.
```

Types can be precise. Make them so.

### 11. Prefer function overloads to union parameters.
Wrong:
```typescript
function createElement(tag: 'img' | 'input' | 'div', props?: any): HTMLElement {
  // Complex conditional logic
}
```
Right:
```typescript
function createElement(tag: 'img', props: ImgProps): HTMLImageElement;
function createElement(tag: 'input', props: InputProps): HTMLInputElement;
function createElement(tag: 'div', props: DivProps): HTMLDivElement;
function createElement(tag: string, props: any): HTMLElement {
  // Implementation
}
```

Overloads provide clarity at the call site.

### 12. Name generic parameters meaningfully.
Wrong:
```typescript
function map<T, U>(items: T[], fn: (item: T) => U): U[]
```
Right:
```typescript
function map<Input, Output>(
  items: Input[], 
  fn: (item: Input) => Output
): Output[]
```

Even type parameters deserve meaningful names.

## IV. Words and Expressions Commonly Misused

### 13. interface vs type
Interfaces can be extended and augmented. Types cannot be changed once defined.

Use interface when you expect extension:
```typescript
interface Animal {
  name: string;
}
interface Dog extends Animal {
  breed: string;
}
```

Use type for unions and fixed definitions:
```typescript
type Result<T> = Success<T> | Failure;
```

### 14. enum vs const object
Wrong:
```typescript
enum Status {
  Active = 'ACTIVE',
  Inactive = 'INACTIVE'
}
```
Right:
```typescript
const Status = {
  Active: 'ACTIVE',
  Inactive: 'INACTIVE'
} as const;

type Status = typeof Status[keyof typeof Status];
```

Enums are TypeScript's mistake. Const objects are JavaScript's solution.

### 15. null vs undefined
TypeScript distinguishes them. So should you.

- `undefined`: not yet assigned
- `null`: intentionally empty

Enable `strictNullChecks` and handle both explicitly.

## V. An Approach to Style

### 16. Omit needless type annotations.
Wrong:
```typescript
const add = (a: number, b: number): number => {
  const sum: number = a + b;
  return sum;
};
```
Right:
```typescript
const add = (a: number, b: number) => {
  return a + b;
};
```

TypeScript infers the return type. Let it.

### 17. Use utility types.
Wrong:
```typescript
interface TodoUpdate {
  title?: string;
  completed?: boolean;
  description?: string;
}
```
Right:
```typescript
interface Todo {
  title: string;
  completed: boolean;
  description: string;
}

type TodoUpdate = Partial<Todo>;
```

TypeScript provides tools. Use them: `Partial`, `Required`, `Pick`, `Omit`, `Record`.

### 18. Narrow types progressively.
Wrong:
```typescript
function process(value: string | number | null) {
  return (value as string).toUpperCase(); // Dangerous assertion
}
```
Right:
```typescript
function process(value: string | number | null) {
  if (value === null) {
    return '';
  }
  if (typeof value === 'number') {
    return String(value);
  }
  return value.toUpperCase(); // TypeScript knows it's string
}
```

Guide the compiler through your logic.

### 19. Use generics for reusability, not complexity.
Wrong:
```typescript
type ComplexType<T, K extends keyof T, V extends T[K]> = 
  T extends Record<K, V> 
    ? V extends string 
      ? T 
      : never 
    : never;
```
Right:
```typescript
type ValueOf<T> = T[keyof T];
```

Generics should clarify, not obscure.

### 20. Export types separately.
Wrong:
```typescript
export default class User {
  name: string;
}
```
Right:
```typescript
export interface UserData {
  name: string;
}

export class User implements UserData {
  name: string;
}
```

Types are contracts. Make them explicit and importable.

## VI. Final Reminders

**The type system is your friend.** Work with it, not against it.

**Start with types, then implement.** Design the contract before the code.

**Avoid type assertions.** If you need `as`, question your types.

**Use `noImplicitAny`.** Implicit any is surrendering to JavaScript.

**Let errors guide you.** TypeScript errors are not obstacles; they are guardrails.

**Write types for your future self.** Complex clever types become tomorrow's mystery. Prefer clarity.
