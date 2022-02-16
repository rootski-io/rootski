import { Tooltip, withStyles } from "@material-ui/core";
import React from "react";
import { Theme } from "@material-ui/core/styles";

export const HTMLTooltip = withStyles((theme: Theme) => ({
  tooltip: {
    backgroundColor: "#f5f5f9",
    color: "rgba(0, 0, 0, 0.87)",
    maxWidth: 220,
    border: "1px solid #dadde9",
    margin: "0px",
    padding: "0px",
    fontSize: theme.typography.pxToRem(12),
  },
}))(Tooltip);
