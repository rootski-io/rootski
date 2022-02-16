import { Card, CardContent, Typography, Theme } from "@material-ui/core";
import React from "react";
import { makeStyles } from "@material-ui/core/styles";

interface WordPageSectionProps {
  title: string;
  children: Array<JSX.Element | null>;
}

const useStyles = makeStyles((theme: Theme) => ({
  sectionHeading: {
    marginTop: "2rem",
  },
  // definitionLink: {
  //   marginRight: "0.5rem",
  //   marginBottom: "0.5rem",
  // },
}));

export const WordPageSection = (props: WordPageSectionProps) => {
  const classes = useStyles();

  return (
    <>
      <Typography
        color="primary"
        variant="h5"
        className={classes.sectionHeading}
      >
        {props.title}
      </Typography>

      <Card>
        <CardContent>{props.children}</CardContent>
      </Card>
    </>
  );
};
