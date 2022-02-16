import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import Typography from "@material-ui/core/Typography";
import { v4 as uuidv4 } from "uuid";
import Paper from "@material-ui/core/Paper";

/**
 *  Styles
 */

const useStyles = makeStyles({
  highlightable: {
    fontSize: "2rem",
    marginRight: "0.2rem",
    "&::selection": {
      background: "lightgreen",
    },
  },
});

/**
 * Helper Component
 */

export interface HighlightableProps {
  text: string;
  selectionHandler(
    beginning: string,
    highlighted: string,
    end: string,
    hash: string
  ): any;
  hash: string;
}

// clear any text highlights in the browser window
const clearSelection = () => {
  const selectionObj = window.getSelection();
  if (selectionObj) selectionObj.removeAllRanges();
};

//
// A basic text component that handles onMouseUp events using
// a :selectionHandler: prop.
//
export const Highlightable = (props: HighlightableProps) => {
  const classes = useStyles();

  /**
   * Handle the onMouseUp event in the component. If the text is
   *     "discombobulated"
   * and the highlight is "combo", i.e.
   *     dis-combo-bulated
   * then this function ends by calling
   *     props.selectionHandler("dis", "combo", "bulated")
   * @param e {onMouseUpEvent}
   */
  const getSelection = (e: any) => {
    e.preventDefault();

    /**
    Get a selection object and all of its properties after selecting the text.
    If any of the properties don't exist, clear the selection and cancel.
    */
    const selectionObj = window.getSelection && window.getSelection();

    if (!selectionObj) {
      clearSelection();
      console.log("No selection object");
      return;
    }
    const selection = selectionObj.toString();
    const anchorNode = selectionObj.anchorNode;
    if (!anchorNode) {
      clearSelection();
      console.log("No selection: no anchor node");
      return;
    }
    const focusNode = selectionObj.focusNode;
    if (!focusNode) {
      clearSelection();
      console.log("No selection: no focus node");
      return;
    }
    const anchorOffset = selectionObj.anchorOffset;
    const focusOffset = selectionObj.focusOffset;
    const position = anchorNode.compareDocumentPosition(focusNode);

    // cancel if the select didn't start and end in the same HTML node
    if (anchorNode != focusNode) {
      clearSelection();
      console.log("Selection did not start and end in the same HTML node");
      return;
    }

    // determine whether the highlight went from right to left or left to right
    let forward = false;
    if (position === anchorNode.DOCUMENT_POSITION_FOLLOWING) {
      forward = true;
    } else if (position === 0) {
      forward = focusOffset - anchorOffset > 0;
    }

    // based on the above right-left/left-right, determine the start of the selection
    let selectionStart = forward ? anchorOffset : focusOffset;

    // slice up the component text into beginning-highlighted-end
    const selectionEnd = selectionStart + selection.length;
    const beginning = props.text.slice(0, selectionStart);
    const highlighted = props.text.slice(selectionStart, selectionEnd);
    const end = props.text.slice(selectionEnd);

    // pass these values to be used outside of the Highlightable component
    return props.selectionHandler(beginning, highlighted, end, props.hash);
  };

  return (
    <Typography
      display="inline"
      onMouseUp={getSelection}
      className={classes.highlightable}
    >
      {props.text}
    </Typography>
  );
};
