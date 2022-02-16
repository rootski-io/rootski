import React from "react";
import { Typography, Grid } from "@material-ui/core";

// special create-react-app method of turning SVGs into React components
import { ReactComponent as CliffSVG } from "./../../../assets/images/cliff.svg";
import { ReactComponent as BreakdownWindowSVG } from "./../../../assets/images/breakdown-window.svg";
import GreenDividerSVG from "./../../../assets/images/green-divider.svg";
import { ReactComponent as LogoColorSVG } from "./../../../assets/images/rootski-logo-color.svg";
import { ReactComponent as DownArrowSVG } from "./../../../assets/images/down-arrow.svg";
import { ReactComponent as HardAlphabetSVG } from "./../../../assets/images/hard-alphabet.svg";
import { ReactComponent as ManyLongWordsSVG } from "./../../../assets/images/many-long-words.svg";
import { ReactComponent as ManySimilarWordsSVG } from "./../../../assets/images/many-similar-words.svg";

// CSS classes
import cliffAndIntroClasses from "./cliff-and-intro.module.css";
import downArrowClasses from "./down-arrow.module.css";
import supportingPointClasses from "./supporting-points.module.css";

import { BreakdownSlider } from "./BreakdownSlider";

export const LandingPage = () => {
  return (
    <>
      <div
        style={{
          overflow: "hidden",
        }}
      >
        <div
          style={{
            position: "relative",
            width: "100%",
            marginBottom: "150px",
            maxHeight: "100%",
            maxWidth: "1600px",
          }}
        >
          <CliffSVG className={cliffAndIntroClasses.cliffSVG} />
          <div className={cliffAndIntroClasses.rootskiIntro}>
            <LogoColorSVG />
            <Typography>
              Climb the mountain of Russian
              <br />
              vocabulary with roots and A.I.
            </Typography>
          </div>
        </div>
      </div>

      <div className={downArrowClasses.downArrowContainer}>
        <Typography>What?</Typography>
        <DownArrowSVG className={downArrowClasses.downArrow} />
      </div>

      <div style={{ height: "400px" }}></div>

      <div
        style={{
          display: "flex",
          alignItems: "center",
          flexDirection: "column",
          width: "100%",
          backgroundImage: `url(${GreenDividerSVG})`,
          backgroundRepeat: "no-repeat",
          backgroundSize: "auto 100%",
        }}
      >
        <BreakdownWindowSVG
          style={{
            zIndex: 2,
            position: "relative",
            maxWidth: "1000px",
            transform: "translateY(-240px)",
          }}
        />

        <div
          style={{
            color: "white",
            transform: "translateY(-160px)",
            textAlign: "center",
          }}
        >
          <Typography style={{ fontSize: "30px", marginBottom: "10px" }}>
            Learning Russian words is easy when you know how to break them into
            roots.
          </Typography>
          <Typography style={{ fontSize: "30px" }}>Let's see how!</Typography>
        </div>
      </div>

      <div
        style={{
          paddingTop: "40px",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
        }}
      >
        <Typography variant="h2" style={{ textAlign: "center" }}>
          First, let's look at what makes learning Russian words hard.
        </Typography>
        <RowGrid
          reversed
          graphicComponent={<HardAlphabetSVG />}
          explanationComponent={
            <>
              <Typography variant="h4">There's the crazy alphabet.</Typography>
              <Typography>
                Not to mention all the consonants strung together.
              </Typography>
            </>
          }
        />
        <RowGrid
          graphicComponent={<ManyLongWordsSVG />}
          explanationComponent={
            <Typography variant="h4">
              Many Russian words are LOOOooOOng.
            </Typography>
          }
        />
        <RowGrid
          reversed
          graphicComponent={<ManySimilarWordsSVG />}
          explanationComponent={
            <>
              <Typography variant="h4">
                Tons of words have confusingly similar spellings.
              </Typography>
            </>
          }
        />
      </div>
    </>
  );
};

interface RowGridProps {
  graphicComponent: JSX.Element;
  explanationComponent: JSX.Element;
  reversed?: boolean;
}

const RowGrid = (props: RowGridProps) => {
  const graphicItem = (
    <Grid item xs={6}>
      {props.graphicComponent}
    </Grid>
  );

  const explanationItem = (
    <Grid item xs={6}>
      {props.explanationComponent}
    </Grid>
  );

  const gridItems: Array<JSX.Element> = !props.reversed
    ? [graphicItem, explanationItem]
    : [explanationItem, graphicItem];

  return (
    <Grid
      container
      spacing={4}
      direction={"row"}
      alignItems={"center"}
      style={{ maxWidth: "100%", padding: "20px" }}
    >
      {gridItems}
    </Grid>
  );
};
