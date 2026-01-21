Download the React DevTools for a better development experience: https://react.dev/link/react-devtools
forward-logs-shared.ts:95 [HMR] connected
react-dom-client.development.js:5530 Uncaught Error: Hydration failed because the server rendered HTML didn't match the client. As a result this tree will be regenerated on the client. This can happen if a SSR-ed Client Component used:

- A server/client branch `if (typeof window !== 'undefined')`.
- Variable input such as `Date.now()` or `Math.random()` which changes each time it's called.
- Date formatting in a user's locale which doesn't match the server.
- External changing data without sending a snapshot of it along with the HTML.
- Invalid HTML tag nesting.

It can also happen if the client has a browser extension installed which messes with the HTML before React loaded.

https://react.dev/link/hydration-mismatch

  ...
    <ErrorBoundary errorComponent={undefined} errorStyles={undefined} errorScripts={undefined}>
      <LoadingBoundary name="/" loading={null}>
        <HTTPAccessFallbackBoundary notFound={<SegmentViewNode>} forbidden={undefined} unauthorized={undefined}>
          <HTTPAccessFallbackErrorBoundary pathname="/dashboard" notFound={<SegmentViewNode>} forbidden={undefined} ...>
            <RedirectBoundary>
              <RedirectErrorBoundary router={{...}}>
                <InnerLayoutRouter url="/dashboard" tree={[...]} params={{}} cacheNode={{...}} segmentPath={[...]} ...>
                  <SegmentViewNode type="layout" pagePath="/phase-3-c...">
                    <SegmentTrieNode>
                    <script>
                    <script>
                    <DashboardLayout>
                      <ChatWidgetProvider>
                        <div className="min-h-scre...">
                          <Navigation>
                            <nav
+                             className="bg-gradient-to-r from-blue-600 to-indigo-600 shadow-lg"
-                             className="bg-white shadow-sm border-b"
                            >
                              <div className="max-w-7xl ...">
                                <div className="flex justi...">
                                  <div
+                                   className="flex items-center space-x-8"
-                                   className="h-6 w-32 bg-gray-200 animate-pulse rounded"
                                  >
+                                   <div className="flex items-center space-x-2">
                                    ...
                                  ...
                          ...
                ...

    at throwOnHydrationMismatch (react-dom-client.development.js:5530:11)
    at beginWork (react-dom-client.development.js:12385:17)
    at runWithFiberInDEV (react-dom-client.development.js:986:30)
    at performUnitOfWork (react-dom-client.development.js:18997:22)
    at workLoopConcurrentByScheduler (react-dom-client.development.js:18991:9)
    at renderRootConcurrent (react-dom-client.development.js:18973:15)
    at performWorkOnRoot (react-dom-client.development.js:17834:11)
    at performWorkOnRootViaSchedulerTask (react-dom-client.development.js:20384:7)
    at MessagePort.performWorkUntilDeadline (scheduler.development.js:45:48)
throwOnHydrationMismatch @ react-dom-client.development.js:5530
beginWork @ react-dom-client.development.js:12385
runWithFiberInDEV @ react-dom-client.development.js:986
performUnitOfWork @ react-dom-client.development.js:18997
workLoopConcurrentByScheduler @ react-dom-client.development.js:18991
renderRootConcurrent @ react-dom-client.development.js:18973
performWorkOnRoot @ react-dom-client.development.js:17834
performWorkOnRootViaSchedulerTask @ react-dom-client.development.js:20384
performWorkUntilDeadline @ scheduler.development.js:45
<div>
exports.jsxDEV @ react-jsx-dev-runtime.development.js:342
Navigation @ Navigation.tsx:43
react_stack_bottom_frame @ react-dom-client.development.js:28038
renderWithHooksAgain @ react-dom-client.development.js:8084
renderWithHooks @ react-dom-client.development.js:7996
updateFunctionComponent @ react-dom-client.development.js:10501
beginWork @ react-dom-client.development.js:12085
runWithFiberInDEV @ react-dom-client.development.js:986
performUnitOfWork @ react-dom-client.development.js:18997
workLoopConcurrentByScheduler @ react-dom-client.development.js:18991
renderRootConcurrent @ react-dom-client.development.js:18973
performWorkOnRoot @ react-dom-client.development.js:17834
performWorkOnRootViaSchedulerTask @ react-dom-client.development.js:20384
performWorkUntilDeadline @ scheduler.development.js:45Understand this error
favicon.ico:1  GET http://localhost:3000/favicon.ico 404 (Not Found)Understand this error