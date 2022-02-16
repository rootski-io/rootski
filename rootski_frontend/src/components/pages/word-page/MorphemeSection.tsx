import React from "react";
import { Typography } from "@material-ui/core";
import { Breakdown, Morpheme, MorphemeType } from "../../../models/models";
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import { MORPHEME_COLORS } from "../../../config/colors";
import { makeStyles, Theme } from "@material-ui/core/styles";
import ListItem from "@material-ui/core/ListItem";
import List from "@material-ui/core/List";
import { MorphemeListItem } from "../../breakdown/MorphemeListItem";

interface MorphemeSectionProps {
  breakdown: Breakdown;
  sectionHeadingClassName: string;
}

export const MorphemeSection = (props: MorphemeSectionProps) => {
  const { breakdown, sectionHeadingClassName } = props;
  return (
    <>
      <Typography
        color="primary"
        variant="h5"
        className={sectionHeadingClassName}
      >
        Morphemes in Breakdown
      </Typography>
      <Card>
        <CardContent>
          <List>
            {breakdown.breakdown_items
              .filter((m: Morpheme) => m.type !== null)
              .map((m: Morpheme, index: number) => (
                <MorphemeListItem morpheme={m} />
              ))}
          </List>
        </CardContent>
      </Card>
    </>
  );
};
