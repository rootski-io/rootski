//
// This file contains all of the URL routes used with react-router-dom in this app
//

// Word Page Route Flow:
//     1. history.push("/word/1/preposition") is called from anywhere the app (including by putting it in the search bar)
//     2. in App.tsx, the <Switch> element with the <Route children={WordPageRouteHandler}> is called
//     3. the <WordPageRouteHandler> element is rendered
//          a. the useParams() hook is used to extract
//             { word_type: "preposition", word_id: 1, word: "в" } from the route
//          b. returns a <WordPage word_id={1} word_type={"preposition"} />
//     4. <WordPage> uses the word_id and word_type to fetch the WordData and display the page!
export const WORD_PAGE_ROUTE = "/word/:word_id/:word_type";
