import React from "react";
import { makeStyles, createStyles } from "@material-ui/core/styles";
import Typography from "@material-ui/core/Typography";
import { Theme } from "@material-ui/core";
import { theme } from "../theme";
import { Morpheme } from "../../models/models";
import { MORPHEME_COLORS } from "../../config/colors";

interface MorphemeTagProps {
  morpheme: Morpheme;
}

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    // nifty trick: the "tag" class is actually a function that takes a props argument
    // so that the morpheme color can be assigned dynamically based on the morpheme type
    tag: (props: MorphemeTagProps) => {
      return {
        color: props.morpheme.type
          ? MORPHEME_COLORS[props.morpheme.type]
          : "black",
        paddingRight: "0.25rem",
      };
    },
  })
);

export default function MorphemeTag(props: MorphemeTagProps) {
  const classes = useStyles(props);
  const { morpheme } = props;

  return (
    <Typography className={classes.tag} variant="h4" display="inline">
      {morpheme.morpheme}
    </Typography>
  );
}
