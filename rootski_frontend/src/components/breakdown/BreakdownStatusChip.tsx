import React from "react";
import OfflineBoltIcon from "@material-ui/icons/OfflineBolt";
import CheckCircleIcon from "@material-ui/icons/CheckCircle";
import FavoriteIcon from "@material-ui/icons/Favorite";
import EmojiEmotionsIcon from "@material-ui/icons/EmojiEmotions";
import ErrorIcon from "@material-ui/icons/Error";
import { Typography } from "@material-ui/core";
import { blue, green, orange, red, yellow } from "@material-ui/core/colors";
import Paper from "@material-ui/core/Paper";
import { HTMLTooltip } from "../HTMLTooltip";

const ICON_COLOR_WEIGHT = 500;

interface IconChipProps {
  iconColor: string;
  icon(props: any): JSX.Element;
  text: string;
  tooltip: JSX.Element;
  extraPaperStyles?: React.CSSProperties;
}

const IconChip = (props: IconChipProps) => {
  const { iconColor, icon, text } = props;
  const Icon = icon;

  const extraPaperStyles = props.extraPaperStyles || {};
  const containerStyles: React.CSSProperties = {
    display: "flex",
    flexDirection: "column",
    justifyContent: "flex-end",
    alignItems: "center",
    width: "50px",
    backgroundColor: "clear",
    borderRadius: "10px",
    paddingInline: "15px",
    marginRight: "10px",
  };
  const iconStyles: React.CSSProperties = {
    color: iconColor,
    fontSize: "50px",
    marginBlockEnd: "-10px",
  };
  return (
    // @ts-ignore
    <HTMLTooltip
      title={
        <Paper style={{ padding: "15px", ...extraPaperStyles }}>
          {props.tooltip}
        </Paper>
      }
    >
      <div style={containerStyles}>
        <div style={iconStyles}>
          <Icon fontSize={"default"} />
        </div>
        <div>
          <Typography style={{ textAlign: "center" }} variant={"subtitle2"}>
            {text}
          </Typography>
          <br />
        </div>
      </div>
    </HTMLTooltip>
  );
};

export interface BreakdownStatusChipProps {
  wordFrequency?: number;

  type:
    | "verified"
    | "unverified"
    | "community"
    | "inference"
    | "submitted-by-user"
    | "frequency";
}

export const BreakdownStatusChip = (
  props: BreakdownStatusChipProps
): JSX.Element => {
  const type: string = props.type;
  switch (type) {
    case "verified":
      return (
        <IconChip
          text={"Verified Breakdown"}
          icon={CheckCircleIcon}
          iconColor={green[ICON_COLOR_WEIGHT]}
          tooltip={
            <>
              <Typography>
                This breakdown has been reviewed by an experienced community
                member and deemed worthy! 🎉 🎉 🎉
              </Typography>
            </>
          }
        />
      );
    case "unverified":
      return (
        <IconChip
          text={"Breakdown Unverified"}
          icon={ErrorIcon}
          iconColor={orange[300]}
          tooltip={
            <>
              <Typography>
                Experienced community members periodically review breakdowns and
                approve them. ✅
              </Typography>
              <br />
              <Typography>
                If your breakdown is verified this way, it will become official
                and everyone will see it!
              </Typography>
            </>
          }
        />
      );
    case "community":
      return (
        <IconChip
          text={"Community Submission"}
          icon={FavoriteIcon}
          iconColor={red[400]}
          tooltip={
            <>
              <Typography>
                Someone else submitted a breakdown for this word!
              </Typography>
              <br />
              <Typography>
                You will always see these over a guess by the Rootski AI.
              </Typography>
            </>
          }
        />
      );
    case "inference":
      return (
        <IconChip
          text={"Rootski AI Inference"}
          icon={OfflineBoltIcon}
          iconColor={blue[ICON_COLOR_WEIGHT]}
          tooltip={
            <>
              <Typography>
                When a word does not have a breakdown, Rootski makes a guess
                using AI.
              </Typography>
              <br />
              <Typography>
                As the community submits breakdowns, Rootski learns and improves
                at guessing.
              </Typography>
            </>
          }
        />
      );
    case "submitted-by-user":
      return (
        <IconChip
          text={"Submitted by you"}
          icon={EmojiEmotionsIcon}
          iconColor={blue[300]}
          tooltip={
            <>
              <Typography>You're amazing! ❤️</Typography>
              <br />
              <Typography>
                You are shown your own breakdowns instead of breakdowns
                submitted by the community or the Rootski AI.
              </Typography>
              <br />
              <Typography>
                If a breakdown is verified, it is always shown.
              </Typography>
            </>
          }
        />
      );
    case "frequency":
      const wordFrequency = props.wordFrequency as number;
      return (
        <IconChip
          text={"Frequency Ranking"}
          icon={(props: IconChipProps) => (
            <Typography style={{ marginBottom: "10px" }}>
              <strong>{wordFrequency}</strong>
            </Typography>
          )}
          iconColor={"none"}
          extraPaperStyles={{ width: "300px" }}
          tooltip={
            <>
              <Typography>
                This says how frequently a given Russian word is used.
              </Typography>
              <br />
              <Typography>
                <strong>1</strong> is the most common word, <strong>2</strong>{" "}
                is the second most common, etc.
              </Typography>
              <br />
              <Typography>
                This ranking was created by processing millions of words of
                Russian text and counting the number of times each word showed
                up.
              </Typography>
              <br />
              <Typography>
                Knowing the frequency can help you know if a word is worth
                memorizing/using－especially if you're comparing multiple
                synonyms.
              </Typography>
            </>
          }
        />
      );
    default:
      return <></>;
  }
};
