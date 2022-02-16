import React from "react";
import { Morpheme } from "../../models/models";
import List from "@material-ui/core/List";
import MenuItem from "@material-ui/core/MenuItem";
import Divider from "@material-ui/core/Divider";
import ListItem, { ListItemProps } from "@material-ui/core/ListItem";
import ListItemIcon from "@material-ui/core/ListItemIcon";
import Typography from "@material-ui/core/Typography";
import ListItemText from "@material-ui/core/ListItemText";
import { makeStyles, createStyles } from "@material-ui/core/styles";
import { MORPHEME_COLORS } from "../../config/colors";
import { Theme } from "@material-ui/core";
import { MorphemeListItem } from "./MorphemeListItem";

const useStylesMorphemeListItem = makeStyles((theme: Theme) =>
  createStyles({
    morphemeText: (props: MorphemePickerListItemProps) => {
      const textColor = props.morpheme.type
        ? MORPHEME_COLORS[props.morpheme.type]
        : "gray";
      return {
        color: textColor,
      };
    },
  })
);

interface MorphemePickerListItemProps {
  morpheme: Morpheme;
  onClickMorpheme(morpheme: Morpheme): any;
}

const MorphemePickerListItem = (props: MorphemePickerListItemProps) => {
  const { morpheme } = props;

  if (morpheme.type && morpheme.morpheme_id) {
    return (
      <MorphemeListItem
        morpheme={morpheme}
        onClickMorpheme={() => props.onClickMorpheme(morpheme)}
      />
    );
  } else {
    return (
      <ListItem button onClick={() => props.onClickMorpheme(morpheme)}>
        <ListItemText style={{ color: "gray" }}>Not a root...</ListItemText>
      </ListItem>
    );
  }
};

export interface MorphemePickerProps {
  morphemes: Array<Morpheme>;
  onClickMorpheme(morpheme: Morpheme): any;
}

const useStylesMorphemePicker = makeStyles({
  morphemePickerContainer: {
    marginTop: "2rem",
    width: "100%",
  },
});

export const MorphemePicker = (props: MorphemePickerProps) => {
  const classes = useStylesMorphemePicker();

  return (
    <div className={classes.morphemePickerContainer}>
      <Typography>Select an option:</Typography>
      <Divider />
      <List>
        {props.morphemes.map((morpheme: Morpheme) => (
          <MorphemePickerListItem
            morpheme={morpheme}
            onClickMorpheme={props.onClickMorpheme}
          />
        ))}
      </List>
    </div>
  );
};
