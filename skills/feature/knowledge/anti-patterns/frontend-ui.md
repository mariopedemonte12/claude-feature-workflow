# Seed catalog: component-based UIs

For React, Vue, Svelte, Angular, Solid and similar front ends.

| Seed | Smell | Why it hurts | Instead | Detect |
| --- | --- | --- | --- | --- |
| UI-01 | God component: fetching, state, business rules and markup in one component | Untestable; every change re-renders and risks everything | Split data access, logic (hooks or composables) and presentation | File and function length; manual |
| UI-02 | Derived state stored and synced with an effect | Extra renders and stale values | Compute it during render or memoize | ESLint (react-hooks, react-you-might-not-need-an-effect); ast-grep |
| UI-03 | Prop drilling through components that do not use the prop | Every intermediate component changes with the data | Composition (children/slots) or scoped context | Manual |
| UI-04 | Server data copied into global client state | Two sources of truth; stale caches | A server-cache library or the framework's data loading | Manual |
| UI-05 | Effects without cleanup or with missing dependencies | Leaks, race conditions, stale closures | Cleanup functions; correct dependencies; abort controllers | ESLint react-hooks/exhaustive-deps |
| UI-06 | Index as list key for reorderable lists | Wrong item state after reordering | Stable ids as keys | ESLint react/no-array-index-key |
| UI-07 | Inaccessible interactive elements (`div` with click handlers, images without alt, inputs without labels) | Keyboard and screen-reader users are blocked | Native elements and labels | eslint-plugin-jsx-a11y, vuejs-accessibility; axe in E2E |
| UI-08 | Business rules inside UI components | Rules duplicated across screens and untested | Pure functions in the feature, called by the UI | Manual |
| UI-09 | Hand-built widgets for what the platform or design system provides | More code, worse accessibility | The house component or the native element | Manual |
| UI-10 | Styles with magic values outside the design tokens | Inconsistent UI; theme changes miss them | Tokens and variables | Stylelint rules |
