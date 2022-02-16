import React from "react";
import { createStyles, makeStyles, Theme } from "@material-ui/core/styles";
import CircularProgress from "@material-ui/core/CircularProgress";
import { blue, green, red } from "@material-ui/core/colors";
import Button from "@material-ui/core/Button";
import CheckIcon from "@material-ui/icons/Check";
import ReplayIcon from "@material-ui/icons/Replay";
import { Morpheme, WordType } from "../../models/models";
import { RootskiAPIError } from "../../api/errors";
import { useDispatch, useSelector, shallowEqual } from "react-redux";
import { fetchWordDataAction } from "../../redux/actions/WordActions";
import { LoginBeforeSubmitModal } from "./LoginBeforeSubmitModal";
import {
  doSubmitBreakdownRequestWithMorphemes,
  SubmitBreakdownSuccessResponse,
} from "../../api/breakdown";
import { AppState } from "../../redux/reducers";

const REFRESH_WORD_DATA_AFTER_SUBMIT_DELAY_MS = 1000;

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    root: {
      display: "flex",
      alignItems: "center",
    },
    wrapper: {
      position: "relative",
    },
    buttonSuccess: {
      backgroundColor: green[500],
      "&:hover": {
        backgroundColor: green[700],
      },
    },
    buttonFailure: {
      backgroundColor: red[200],
      "&:hover": {
        backgroundColor: red[300],
      },
    },
    buttonDefault: {},
    buttonProgress: {
      color: blue[500],
      position: "absolute",
      top: "50%",
      left: "50%",
      marginTop: -12,
      marginLeft: -12,
    },
  })
);

interface SubmitBreakdownButtonProps {
  morphemes: Array<Morpheme>;
  word_id: number;
  word_type: WordType;

  // run this before submitting to determine whether it is safe to submit
  onClickSubmitPreCheck(): boolean;

  // run this after a successful submission
  onSuccessfulSubmission(): void;
}

export function SubmitBreakdownButton(props: SubmitBreakdownButtonProps) {
  const classes = useStyles();
  const [loading, setLoading] = React.useState(false);
  const [success, setSuccess] = React.useState(false);
  const [failure, setFailure] = React.useState(false);
  const timer = React.useRef<number>();

  React.useEffect(() => {
    return () => {
      clearTimeout(timer.current);
    };
  }, []);

  /**
   * State
   */
  const [showLoginModal, setShowLoginModal] = React.useState(false);

  /**
   * Redux State
   */
  const selectReduxData = (state: AppState) => ({
    authToken: state.authData.idToken,
  });
  const reduxData: ReturnType<typeof selectReduxData> = useSelector(
    selectReduxData,
    shallowEqual
  );
  const userIsLoggedIn: boolean = reduxData.authToken !== null;

  /**
   * Redux Actions
   */
  const dispatch = useDispatch();
  const fetchWordData: ReturnType<typeof fetchWordDataAction> =
    fetchWordDataAction(dispatch);

  /**
   * Helper functions
   */
  const handleButtonClick = () => {
    // display the modal and do nothing more if the user
    // is not logged in
    if (!userIsLoggedIn) {
      setShowLoginModal(true);
      return;
    }

    // if a submission is in process or has already succeeded,
    // we don't want to allow another submission
    if (!loading && !success) {
      // run the pre-check function passed in from the parent to make sure
      // the parent approves of the submission
      const precheckOfBreakdownPassed: boolean = props.onClickSubmitPreCheck();

      // if the pre-check passed, we can submit the breakdown
      if (precheckOfBreakdownPassed) {
        makeSubmitRequest();
      } else {
        // if the pre-check fails, we'll trigger "failure" mode
        setFailure(true);
      }
    }
  };

  /**
   * Submit the breakdown to the server; if successful, fetch the word
   * to cause the WordPage to reload with the new breakdown.
   *
   * This function assumes that the morphemes have been validated
   * (as much as they are ever going to be by the front end)
   * and that the user is logged in (so reduxData.authToken is valid)
   *
   * If the request fails, pop a snackbar explaining why.
   */
  const makeSubmitRequest = async () => {
    const { word_id, word_type, morphemes } = props;

    // put the submit button into a loading state
    setSuccess(false);
    setFailure(false);
    setLoading(true);

    try {
      // make the request
      const response: SubmitBreakdownSuccessResponse =
        await doSubmitBreakdownRequestWithMorphemes(
          word_id,
          morphemes,
          // we assume the user is logged in
          reduxData.authToken as string
        );

      // if successful, put the button into the success state,
      // and issue a page reload request after a short delay
      setSuccess(true);
      setTimeout(() => {
        props.onSuccessfulSubmission();
        fetchWordData(word_id, word_type);
      }, REFRESH_WORD_DATA_AFTER_SUBMIT_DELAY_MS);
    } catch (e) {
      setFailure(true);
      if (typeof e === "object" && "status_code" in e) {
        let error = e as RootskiAPIError;
      } else {
        console.error(e);
      }
    } finally {
      setLoading(false);
    }
  };

  /**
   * Render functions
   */
  const renderLoginModal = () => {
    return (
      <LoginBeforeSubmitModal
        open={showLoginModal}
        handleClose={() => setShowLoginModal(false)}
      />
    );
  };

  /**
   * Final render and return logic
   */
  let buttonClass: any;
  let buttonText: string;
  if (success) {
    buttonText = "Submitted!";
    buttonClass = classes.buttonSuccess;
  } else if (failure) {
    buttonText = "Retry";
    buttonClass = classes.buttonFailure;
  } else {
    buttonText = "Submit for Review";
    buttonClass = classes.buttonDefault;
  }

  return (
    <>
      <span className={classes.wrapper}>
        <Button
          variant={success || failure ? "contained" : "outlined"}
          startIcon={failure && !success ? <ReplayIcon /> : <CheckIcon />}
          color="primary"
          className={buttonClass}
          disabled={loading}
          onClick={handleButtonClick}
        >
          {buttonText}
        </Button>
        {loading && (
          <CircularProgress size={24} className={classes.buttonProgress} />
        )}
      </span>
      {renderLoginModal()}
    </>
  );
}
