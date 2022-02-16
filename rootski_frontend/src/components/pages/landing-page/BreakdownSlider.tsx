import React from "react";
import { ReactComponent as PrefixSliderSVG } from "../../../assets/images/prefix-slider.svg";
import { ReactComponent as RootSliderSVG } from "../../../assets/images/root-slider.svg";
import { ReactComponent as SuffixSliderSVG } from "../../../assets/images/suffix-slider.svg";
import { ReactComponent as SliderCoverSVG } from "../../../assets/images/slider-cover.svg";
import { ReactComponent as BreakdownSliderSVG } from "../../../assets/images/breakdown-slider.svg";

import moduleClasses from "./breakdown-slider.module.css";

export const BreakdownSlider = () => {
  return (
    <>
      <BreakdownSliderSVG />
    </>
  );
};

// export const BreakdownSlider = () => {
//     return(
//     <>
//     <div style={{marginTop: "100px"}}></div>

//     <div className={moduleClasses.wrapper}>
//         <SliderCoverSVG className={moduleClasses.sliderCover}/>
//         <div className={moduleClasses.slidersContainer}>
//             <PrefixSliderSVG className={moduleClasses.slider} />
//             <RootSliderSVG className={moduleClasses.slider} />
//             <SuffixSliderSVG className={moduleClasses.slider} />
//         </div>
//     {/* <RootSliderSVG /> */}
//     </div>
//     </>
//     )
// }
