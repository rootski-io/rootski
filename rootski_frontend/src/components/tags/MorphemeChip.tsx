import React from "react";
import { makeStyles, createStyles } from "@material-ui/core/styles";
import Typography from "@material-ui/core/Typography";
import Chip from "@material-ui/core/Chip";
import { Theme } from "@material-ui/core";
import { theme } from "../theme";
import { Morpheme } from "../../models/models";
import {
  MORPHEME_COLORS,
  MORPHEME_COLORS_TRANSPARENT,
} from "../../config/colors";

interface MorphemeChipProps {
  morpheme: Morpheme;

  // Chip props
  label: string;
  onDelete(): any;
}

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    // nifty trick: the "chip" class is actually a function that takes a props argument
    // so that the morpheme color can be assigned dynamically based on the morpheme type
    chip: (props: MorphemeChipProps) => {
      const solidColor = props.morpheme.type
        ? MORPHEME_COLORS[props.morpheme.type]
        : "";
      const transparentColor = props.morpheme.type
        ? MORPHEME_COLORS_TRANSPARENT[props.morpheme.type]
        : "";
      return {
        color: solidColor,
        borderColor: solidColor,
        backgroundColor: transparentColor,
        fontSize: "2rem",
        // marginBottom: "0.75rem",
        "& span": {
          // fix the button being off-center from the cyrillic text
          paddingBottom: "0.5rem",
        },
        marginRight: "0.2rem",
        marginTop: "10px",
      };
    },
  })
);

export function MorphemeChip(props: MorphemeChipProps) {
  const classes = useStyles(props);

  return (
    <Chip
      label={props.label}
      className={classes.chip}
      variant="outlined"
      onDelete={props.onDelete}
    />
  );
}
