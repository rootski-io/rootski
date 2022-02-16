import React from "react";
import { Typography } from "@material-ui/core";
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import { makeStyles, Theme } from "@material-ui/core/styles";
import ListItem, { ListItemProps } from "@material-ui/core/ListItem";
import List from "@material-ui/core/List";
import { Morpheme } from "../../models/models";
import { MORPHEME_COLORS } from "../../config/colors";
import { HTMLTooltip } from "../HTMLTooltip";
import Paper from "@material-ui/core/Paper";
import HelpIcon from "@material-ui/icons/Help";

const useStyles = makeStyles((theme: Theme) => ({
  listItemContainer: {
    display: "flex",
    flexDirection: "row",
    justifyContent: "space-between",
  },
  listItemColumn: {
    display: "flex",
    flexDirection: "column",
    justifyContent: "space-around",
  },
}));

interface MorphemeListItemProps {
  morpheme: Morpheme;
  onClickMorpheme?: (morpheme: Morpheme) => void;
}

declare global {
  namespace JSX {
    interface IntrinsicElements {
      font: any;
    }
  }
}

export const MorphemeListItem = (props: MorphemeListItemProps) => {
  const { morpheme } = props;

  const classes = useStyles();

  // props validation (to make typescript happy)
  console.log("rendering morpheme LI for", props.morpheme);
  if (morpheme.type === null)
    throw Error("got null morpheme type morpheme list item");

  const levelText: string = ![-1, null, undefined].includes(morpheme.level)
    ? "" + morpheme.level
    : "6";

  // get a family string that doesn't contain the morpheme in the list item
  const morphemeFamily: string = morpheme.family
    ? morpheme.family
        .split(",")
        .filter((morphemeText: string) => morphemeText !== morpheme.morpheme)
        .join(", ")
    : "";
  const familyMessage = morphemeFamily ? "(other forms) " + morphemeFamily : "";
  const morphemeTypePrefix =
    morpheme.word_pos !== "any" ? morpheme.word_pos + " " : "";

  const renderMeaning = ({ meaning }: { meaning: string }, index: number) => {
    const meaningPrefix = morpheme.meanings.length > 1 ? `(${index + 1}) ` : "";
    return <Typography>{meaningPrefix + meaning}</Typography>;
  };

  const extraListItemProps =
    props.onClickMorpheme !== undefined
      ? {
          button: true,
          onClick: () => {
            // @ts-ignore
            props.onClickMorpheme(morpheme);
          },
        }
      : {};
  return (
    // @ts-ignore
    <ListItem {...extraListItemProps} className={classes.listItemContainer}>
      <div className={classes.listItemColumn}>
        <Typography>
          <font color={MORPHEME_COLORS[morpheme.type]}>
            {morpheme.morpheme} ({morphemeTypePrefix + morpheme.type})
          </font>{" "}
        </Typography>
        {morpheme.meanings.map(renderMeaning)}
      </div>
      {familyMessage !== "" ? (
        <HTMLTooltip
          title={
            <Paper style={{ padding: "15px" }}>
              <Typography>
                Roots, AKA "morphemes", can have multiple forms with the same
                meaning.
              </Typography>
              <br />
              <Typography>
                Often, the form depends on the morphemes before or after.
              </Typography>
              <br />
              <Typography>
                You can learn which form to use by studying "morphology", or by
                just looking for patterns as you study.
              </Typography>
            </Paper>
          }
        >
          <div
            style={{
              display: "flex",
              flexDirection: "row",
            }}
          >
            <Typography>{familyMessage}&nbsp;&nbsp;</Typography>
            <HelpIcon style={{ color: "gray" }} fontSize={"small"} />
          </div>
        </HTMLTooltip>
      ) : null}
      <HTMLTooltip
        title={
          <Paper
            style={{
              padding: "15px",
            }}
          >
            <Typography>
              Each root (morpheme) in Rootski has a level between{" "}
              <strong>1</strong> and <strong>6</strong>.
            </Typography>
            <br />
            <Typography>
              Level <strong>1</strong> roots are the most basic and should be
              learned first.
            </Typography>
          </Paper>
        }
      >
        <div
          style={{
            display: "flex",
            flexDirection: "row",
          }}
        >
          <Typography>Level {levelText}&nbsp;&nbsp;</Typography>
          <HelpIcon style={{ color: "gray" }} fontSize={"small"} />
        </div>
      </HTMLTooltip>
    </ListItem>
  );
};
