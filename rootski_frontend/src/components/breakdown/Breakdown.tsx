import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import Typography from "@material-ui/core/Typography";
import Divider from "@material-ui/core/Divider";
import MorphemeTag from "../tags/MorphemeTag";
import {
  Breakdown as BreakdownModel,
  Morpheme,
  Word,
} from "../../models/models";
import { v4 as uuidv4 } from "uuid";
import { searchMorphemes } from "../../redux/actions/MorphemeActions";
import { MorphemeChip } from "../tags/MorphemeChip";
import { Highlightable } from "../tags/Highlightable";
import Button from "@material-ui/core/Button";
import { Alert, AlertTitle } from "@material-ui/lab";
import { Link, Slide, Snackbar } from "@material-ui/core";

import CloseIcon from "@material-ui/icons/Close";
import { TransitionProps } from "@material-ui/core/transitions/transition";
import MuiAlert from "@material-ui/lab/Alert";
import { BreakdownStatusChip } from "./BreakdownStatusChip";
import { SubmitBreakdownButton } from "./SubmitBreakdownButton";
import { MorphemePicker } from "./MorphemePicker";

// limit the number of characters in the "Roots containing ..." suggestion
const MAX_SIMILAR_ROOT_CHAR_LENGTH = 200;
const INCOMPLETE_BREAKDOWN_ALERT_DURATION = 11_000; // milliseconds

/**
 *  Styles
 */
const useStyles = makeStyles({
  breakdownCard: {
    marginTop: "2rem",
    marginBottom: "2rem",
  },
  breakdownCardContent: {
    display: "flex",
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    flexWrap: "wrap",
  },
  toggleBreakdownButton: { marginTop: "1rem" },
  breakdownContainer: {
    width: "100%",
    "&:first-child": {
      paddingLeft: "0rem",
    },
    "&:last-child": {
      paddingRight: "1rem",
    },
  },
  similarMorphemesText: {
    marginTop: "1rem",
    color: "gray",
  },
  bold: {
    fontWeight: 700,
    color: "black",
  },
});

/**
 * Breakdown Component
 */

export interface BreakdownProps {
  breakdown: BreakdownModel | null;
  word: Word;

  // these two are a React.useState() pair from the parent
  editBreakdownMode: boolean;
  setEditBreakdownMode: (editBreakdownMode: boolean) => void;
}

// helper function to create a "null morpheme" that will go in the matchedMorphemes list
// whenever text is highlighted. If the Null Morpheme list item is clicked, the highlighted segment
// will become a "null" segment. It's important to fill in the morpheme text correctly so that
// the text inside each labeled Chip adds up to the original word
const getNullMorpheme = (nullMorphemeText: string): Morpheme => ({
  morpheme_id: null,
  morpheme: nullMorphemeText,
  position: -1,
  level: -1,
  meanings: [],
  type: null,
  word_pos: "any",
});

// read the function header string next to see how this is used
type BreakdownDataItem =
  | { type: "chip"; data: ReturnType<typeof MorphemeChip> }
  | { type: "highlightable"; data: ReturnType<typeof Highlightable> };
type BreakdownData = Array<BreakdownDataItem>;

/*
 * Breakdown Component!
 *
 * This component is intense.
 *
 * There are two display modes:
 *   (1) showing the morpheme breakdown as a list of tags; a button offers going into edit mode
 *   (2) showing an edit mode where you
           (a) highlight some text (searchKey)
           (b) the backend API is queried for morphemes matching the searchKey
           (c) a menu of possible results appears
           (d) the selected result becomes a chip
           (e) a save button appears to submit the breakdown to the backend
 *
 * Display Mode (1)
 *    TODO - Fill this out later
 *
 * Display Mode (2)
 *    A :data: array is saved as state. :data: holds 2 types of elements:
 *        1. { type: "highlightable", data: <Highlightable />}
 *        2. { type: "chip", hash: "some-uuid", data: <Chip /> } TODO - make a special chip component that changes color based on whether it is a prefix, root, or suffix
 */
export default function Breakdown(props: BreakdownProps) {
  const classes = useStyles();

  // data is an array of Highlightable's and Chip's
  // you can highlight the highlightable's with the cursor
  // if the highlighted text is a valid morpheme, you can click a button
  // and turn part of the highlightable into a chip. If you delete a chip
  // it turns back into a highlightable and the highlightable's to the right
  // and left are merged together

  // a cleanup function to merge all highlightables to prevent a glitch where
  // 2 or more Highlightables don't merge and ruin the Chip creation process
  const attemptMergeAllHighlightables = () => {
    for (let i = data.length - 1; i > 0; i--) {
      mergeHighlightables(i - 1, i);
    }
  };

  // creates a handler function that will delete a specific chip matching the :chipHash:
  const createOnDeleteChipHandler = (chipHash: string) => {
    return () => {
      // 1. Get the index of the chip in :data:
      const chipIndex = data
        .map((highlightOrChipItem: any) => {
          return highlightOrChipItem.type === "chip"
            ? highlightOrChipItem.hash
            : "not a chip";
        })
        .indexOf(chipHash);

      // 2. Make a new Highlightable from the chip
      const chipItem = data[chipIndex];
      const highlightable = {
        type: "highlightable",
        data: (
          <Highlightable
            text={chipItem.data.props.label}
            hash={uuidv4()}
            selectionHandler={onHighlight}
          />
        ),
      };

      // 3. overwrite the chipIndex place in :data: with the new Highlightable
      const numberOfElementsToDelete = 1;
      data.splice(chipIndex, numberOfElementsToDelete, highlightable);

      // 4. merge any neighboring highlightables with the new one
      mergeHighlightables(chipIndex, chipIndex + 1);
      mergeHighlightables(chipIndex - 1, chipIndex);

      // 5. cause the component to re-render
      setData([...data]);

      // 6. call cleanup method just in case
      attemptMergeAllHighlightables();
    };
  };

  // handles whenever part of a Highlightable is highlighted
  const onHighlight = (
    beginning: string,
    highlighted: string,
    end: string,
    hash: string
  ) => {
    // do nothing if the user just clicked on the word without highlighting
    if (!highlighted) {
      return;
    }

    // make sure the alert about incomplete breakdowns is NOT showing;
    // clearly they know since they are highlighting
    setShowIncompleteBreakdownAlert(false);

    // search for matching and similar morphemes to the higlighted bit
    const searchResults: ReturnType<typeof searchMorphemes> =
      searchMorphemes(highlighted);
    setHighlightData({ beginning, highlighted, end, hash });
    const nullMorpheme = getNullMorpheme(highlighted);
    const matches = [...searchResults.exactMatches, nullMorpheme];
    setMatchedMorphemes(matches);
    setSimilarMorphemes(searchResults.similarMatches);
  };

  // helper function: merge two highlightables in the :data: array
  // NOTE: this DOES NOT trigger a re-render
  const mergeHighlightables = (index1: number, index2: number) => {
    // no point merging if they are the same
    if (index1 === index2) {
      return;
    }

    // can't merge if the indices are bad
    if (
      index1 < 0 ||
      index2 < 0 ||
      index1 >= data.length ||
      index2 >= data.length
    ) {
      return;
    }

    // get the highlights in the right order
    const lower = index1 < index2 ? index1 : index2;
    const upper = index1 > index2 ? index1 : index2;
    const highlight1 = data[lower];
    const highlight2 = data[upper];

    // can't merge if one of them isn't a highlightable
    if (
      highlight1.type !== "highlightable" ||
      highlight2.type !== "highlightable"
    ) {
      return;
    }

    // create the new "merged" highlightable object
    if (
      typeof highlight1.data.props.text != "string" ||
      typeof highlight2.data.props.text != "string"
    ) {
      return;
    }
    const newHighlight = {
      type: "highlightable",
      data: (
        <Highlightable
          text={highlight1.data.props.text + highlight2.data.props.text}
          hash={uuidv4()}
          selectionHandler={onHighlight}
        />
      ),
    };

    // replace the two highlights with the new one
    const numberOfElementsToDelete = 2;
    data.splice(lower, numberOfElementsToDelete, newHighlight);
  };

  /*
   * state
   */
  // initialize the :data: array to a single <Highlightable> containing the word
  const wordText = props.word.word;
  const [data, setData] = React.useState([
    {
      type: "highlightable",
      data: (
        <Highlightable
          text={wordText || "Error: could not find word"}
          selectionHandler={onHighlight}
          hash={uuidv4()}
        />
      ),
    },
  ]);

  // morphemes spelled exactly as selected
  const [matchedMorphemes, setMatchedMorphemes] = React.useState(
    Array<Morpheme>()
  );
  // morphemes containing the selected one
  const [similarMorphemes, setSimilarMorphemes] = React.useState(
    Array<Morpheme>()
  );
  // use :highlightData: to know what is currently highlighted:
  // :hash: is the uuid of the <Highlightable> element that the selection is part of
  //        it is used to know which <Highlightable> to chop up and make into a <MorphemeChip>
  // :beginning:, :highlighted:, and :end: are the substrings of the <Highlightable>
  //        where :highlighted: is the selection, and the complement of :highlighted: are :beginning: and :end:
  const [highlightData, setHighlightData] = React.useState({
    beginning: "",
    highlighted: "",
    end: "",
    hash: "",
  });
  // const [editBreakdownMode, setEditBreakdownMode] = React.useState(false);
  const { editBreakdownMode, setEditBreakdownMode } = props;
  const [showIncompleteBreakdownAlert, setShowIncompleteBreakdownAlert] =
    React.useState(false);

  // helper function to turn breakdown mode off and on
  const toggleBreakdownMode = () => setEditBreakdownMode(!editBreakdownMode);
  // helper function show/hide the snack (alert) on when someone tries to submit before highlighting the whole word

  // use the :beginning:, :highlighted:, and :end: state variables and create a chip!
  const onClickMorpheme = (morpheme: Morpheme) => {
    // deconstruct the state attributes that will be used to create the chip
    const { beginning, highlighted, end, hash } = highlightData;

    // First: Create any new Highlightables and Chips that will go into our array
    const newElements: Array<any> = [];
    if (highlighted) {
      if (beginning) {
        // (1) beginning Highlightable
        newElements.push({
          type: "highlightable",
          data: (
            <Highlightable
              hash={uuidv4()}
              text={beginning}
              // getting recursive now!
              selectionHandler={onHighlight}
            />
          ),
        });
      }

      // (2) The new Chip
      const chipHash = uuidv4();
      newElements.push({
        type: "chip",
        hash: chipHash,
        data: (
          <MorphemeChip
            morpheme={morpheme}
            label={highlighted}
            onDelete={createOnDeleteChipHandler(chipHash)}
          />
        ),
      });

      if (end) {
        // (3) end Highlightable
        newElements.push({
          type: "highlightable",
          data: (
            <Highlightable
              text={end}
              hash={uuidv4()}
              // more recursion!
              selectionHandler={onHighlight}
            />
          ),
        });
      }
    }

    if (newElements.length === 0) {
      return;
    }

    // Second: find the index of the highlighted element that had the onMouseUp event
    const highlightedIndex = data
      // (1) get a list of the Highlightable Hashes or "eric" strings for Chips
      .map((element: any) => {
        return element.type && element.type === "highlightable"
          ? element.data.props.hash
          : "not a highlightable";
      })
      // (2) find the index in the array of the hash from the onMouseUp event
      .indexOf(hash);

    // Third: replace the highlighted elements with all of the new elements
    const numItemsToDelete = 1;
    data.splice(highlightedIndex, numItemsToDelete, ...newElements);

    // Fourth: Merge any adjacent Highlightables in the list
    attemptMergeAllHighlightables();

    // update the breakdown in state
    // EVIL LINE OF CODE!!!!!!! It causes a glitch where deleting a morpheme deletes all the ones after it... no idea why!
    // setData([...data]); // create a new array so that render will be called

    // empty out the suggestions list
    setMatchedMorphemes([]);
    setSimilarMorphemes([]);
  };

  // return a comma separated string of the list of similar morphemes
  const getSimilarMorphemesString = () => {
    let similarMorphemeString = similarMorphemes
      .map((morpheme: Morpheme) => morpheme.morpheme)
      .join(", ");

    similarMorphemeString = similarMorphemeString.substr(
      0,
      MAX_SIMILAR_ROOT_CHAR_LENGTH
    );
    if (similarMorphemeString.length >= MAX_SIMILAR_ROOT_CHAR_LENGTH) {
      similarMorphemeString += "...";
    }

    return similarMorphemeString;
  };

  /**
   * Return true if every character in the word has been made
   * into some sort of Chip.
   *
   * @param {data} Array of <Chip> or <Highlightable> elements (wrapped in an oject)
   */
  const isWholeWordHighlighted = (data: Array<any>) => {
    // if there are any highlightables still in data, then the word is not completely highlighted
    for (let i = 0; i < data.length; i++) {
      if (data[i].type === "highlightable") {
        return false;
      }
    }
    return true;
  };

  /**
   * Logic run using data in this component, before the SubmitBreakdownButton
   * component does its own logic.
   *
   * @returns true if the word is completely highlighted and it is safe
   *   to make a network request to submit the breakdown
   */
  const onClickSubmitPreCheck = (): boolean => {
    if (isWholeWordHighlighted(data)) {
      // if the whole word is highlighted, submit the breakdown
      console.log("User clicked submit. The whole word is highlighted");
      return true;
    } else {
      // otherwise, tell the user what they need to do
      setShowIncompleteBreakdownAlert(true);
      // cause the alert to disappear automatically after a few seconds
      setTimeout(
        () => setShowIncompleteBreakdownAlert(false),
        INCOMPLETE_BREAKDOWN_ALERT_DURATION
      );
      console.log(
        "Incomplete breakdown! User clicked 'submit' too early. Showing breakdown alert:",
        showIncompleteBreakdownAlert
      );
      return false;
    }
  };

  /**
   * JSX for the SnackBar element. Used to pop a snack to the user
   * if they click "Submit for review" in the "Edit breakdown mode"
   * without highlighting the whole word.
   */
  const renderUnfinishedBreakdownSnackbar = () => {
    const unhighlightedPartsOfWord: string = data
      .filter(
        (chipOrHighlightable: any) =>
          chipOrHighlightable.type === "highlightable"
      )
      .map((obj: any): string => obj.data.props.text)
      .join(", ");

    return (
      <Snackbar
        onClick={() => {
          setShowIncompleteBreakdownAlert(false);
        }}
        autoHideDuration={INCOMPLETE_BREAKDOWN_ALERT_DURATION}
        open={showIncompleteBreakdownAlert}
        anchorOrigin={{
          vertical: "top",
          horizontal: "center",
        }}
        TransitionComponent={(props: TransitionProps) => (
          <Slide {...props} direction="down" />
        )}
      >
        <MuiAlert
          elevation={20}
          variant="standard"
          severity="info"
          action={
            <Button
              onClick={() => setShowIncompleteBreakdownAlert(false)}
              variant="text"
              color="primary"
            >
              Yes, Ma'am!
            </Button>
          }
        >
          Oops! You need to label every part of the word before submitting.
          <br />
          You have this left:{" "}
          <Typography variant="overline" color="secondary">
            {unhighlightedPartsOfWord}
          </Typography>
          <br />
          If an unlabeled part isn't a root, go ahead and label it as "Not a
          root".
        </MuiAlert>
      </Snackbar>
    );
  };

  const getMorphemesFromData = (data: BreakdownData): Array<Morpheme> => {
    console.log("the data in the breakdown is", data);
    return data.map((element: BreakdownDataItem, index: number) => {
      if (element.type === "chip") {
        const morpheme: Morpheme = {
          ...element.data.props.morpheme,
          position: index,
        };
        return morpheme;
      } else {
        return {
          ...getNullMorpheme(element.data.props.text),
          position: index,
        };
      }
    });
  };

  const renderBreakdownInEditMode = () => {
    return (
      <>
        <Typography display="block">
          Highlight and label portions of the word:
        </Typography>
        <div
          className={classes.breakdownContainer}
          style={{
            display: "flex",
            flexDirection: "row",
            flexWrap: "wrap",
          }}
        >
          {data.map((component: any) => {
            return <>{component.data}</>;
          })}
          <span
            style={{
              // float: "right",
              marginTop: "10px",
              marginBottom: "20px",
              display: "flex",
              position: "relative",
              marginLeft: "auto",
            }}
          >
            <SubmitBreakdownButton
              word_id={props.word.word_id}
              word_type={props.word.pos}
              // this is VERY awkward: I didn't want the SubmitBreakdownButton to be
              // aware of Chips and Highlightables. I only wanted it to be aware of
              // morphemes... so every time the Breakdown component rerenders, it
              // passes in all the morphemes that have been highlighted *SO FAR*.
              // most of the time, these won't sum to the word. Thus, it's part of
              // onClickSubmitPreCheck's job to make sure the morphemes add up to the word
              // @ts-ignore
              morphemes={getMorphemesFromData(data)}
              onClickSubmitPreCheck={onClickSubmitPreCheck}
              onSuccessfulSubmission={() => setEditBreakdownMode(false)}
            />
            <Button
              onClick={toggleBreakdownMode}
              style={{
                marginLeft: "10px",
              }}
              startIcon={<CloseIcon />}
              variant="outlined"
              color="secondary"
            >
              Cancel{" "}
            </Button>
          </span>
        </div>
        {matchedMorphemes.length > 0 ? (
          <MorphemePicker
            morphemes={matchedMorphemes}
            onClickMorpheme={onClickMorpheme}
          />
        ) : null}
        {similarMorphemes.length > 0 ? (
          <>
            <Divider />
            <div className={classes.similarMorphemesText}>
              <Typography variant="overline">Roots containing</Typography>
              <Typography
                variant="overline"
                className={classes.bold}
              >{` "${highlightData.highlighted}"`}</Typography>
              <Typography variant="overline">{": "}</Typography>
              <Typography variant="overline" display="block">
                {getSimilarMorphemesString()}
              </Typography>
            </div>
          </>
        ) : null}
      </>
    );
  };

  /**
   * Render the breakdown in "display mode"
   *
   * if the breakdown is null or the breakdown is invalid, just show the word
   *
   * @returns JSX for the breakdown in "display mode"
   */
  const renderBreakdown = () => {
    if (props.breakdown !== null) {
      // only display the individual morphemes if they sum to the actual word
      const morphemeSum: string = props.breakdown.breakdown_items
        .map((morpheme: Morpheme) => morpheme.morpheme)
        .join("");
      const showMorphemeTags = props.word.word === morphemeSum;

      if (showMorphemeTags) {
        return (
          <div style={{ marginLeft: "5px" }}>
            {props.breakdown.breakdown_items.map((morpheme: Morpheme) => (
              <MorphemeTag morpheme={morpheme} />
            ))}
          </div>
        );
      }
    }

    // if the morpheme sum isn't valid, just show the word
    return (
      <Typography variant="h4" display="inline">
        {props.word.word}
      </Typography>
    );
  };

  const renderBreakdownStatusArea = (breakdown: BreakdownModel) => {
    // TODO: have the API gather this data
    const { is_inference, is_verified, submitted_by_current_user } = breakdown;
    // a breakdown can be submitted by one of three groups:
    // the user, the AI, or the community
    let submitter: "inference" | "submitted-by-user" | "community";
    if (is_inference) {
      submitter = "inference";
    } else if (submitted_by_current_user) {
      submitter = "submitted-by-user";
    } else {
      submitter = "community";
    }

    return (
      <div
        style={{
          display: "flex",
          flexDirection: "row",
          justifyContent: "flex-end",
          marginLeft: "auto",
        }}
      >
        <BreakdownStatusChip
          type={"frequency"}
          wordFrequency={props.word.frequency}
        />
        <BreakdownStatusChip type={submitter} />
        {is_verified ? (
          <BreakdownStatusChip type="verified" />
        ) : (
          <BreakdownStatusChip type="unverified" />
        )}
      </div>
    );
  };

  const BreakdownInvitation = (props: {
    explanation: string;
    linkText: string;
  }) => {
    const { explanation, linkText } = props;
    return (
      <Alert severity="info">
        <AlertTitle>Info 👋</AlertTitle>
        {explanation}{" "}
        <Link style={{ cursor: "pointer" }} onClick={toggleBreakdownMode}>
          {linkText}
        </Link>{" "}
        😄
        <br />
        <Button
          onClick={toggleBreakdownMode}
          variant="contained"
          color="primary"
          className={classes.toggleBreakdownButton}
        >
          Break it down!
        </Button>
      </Alert>
    );
  };

  const renderBreakdownInvitation = () => {
    // don't invite to do breakdown a breakdown has been verified
    if (props.breakdown !== null && props.breakdown.is_verified) {
      return <></>;
    }

    if (props.breakdown === null) {
      return (
        <BreakdownInvitation
          explanation={"This word has not been broken down yet."}
          linkText={"Give it a go?"}
        />
      );
    } else if (props.breakdown.submitted_by_current_user) {
      return (
        <BreakdownInvitation
          explanation={"This is your breakdown. Want to"}
          linkText={"edit it?"}
        />
      );
    } else if (props.breakdown.is_inference) {
      return (
        <BreakdownInvitation
          explanation={"This breakdown is just an automated guess ⚡️."}
          linkText={"Fix it?"}
        />
      );
    } else {
      return (
        <BreakdownInvitation
          explanation={
            "Someone in the community broke this down ❤️. You may not agree, though."
          }
          linkText={"Submit your own?"}
        />
      );
    }
  };

  return (
    <>
      <Card className={classes.breakdownCard}>
        <CardContent className={classes.breakdownCardContent}>
          {editBreakdownMode ? renderBreakdownInEditMode() : renderBreakdown()}
          {!editBreakdownMode && props.breakdown !== null
            ? renderBreakdownStatusArea(props.breakdown)
            : null}
        </CardContent>
      </Card>
      {editBreakdownMode ? null : renderBreakdownInvitation()}
      {renderUnfinishedBreakdownSnackbar()}
    </>
  );
}
