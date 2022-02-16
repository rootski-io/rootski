import React from "react";
import { Button, Typography } from "@material-ui/core";
import { Modal } from "../Modal";
import { makeStyles } from "@material-ui/core/styles";
import { signInWithCognito } from "../../aws-cognito/auth-utils";

interface LoginBeforeSubmitModalProps {
  // see the descriptions of these on the ModalProps class
  open: boolean;
  handleClose: () => void;
}

const useStyles = makeStyles({
  paragraph: {
    marginBottom: "20px",
  },
  container: {
    padding: "30px",
  },
  signInButton: {
    marginLeft: "20px",
    marginBottom: "25px",
  },
});

export const LoginBeforeSubmitModal = (props: LoginBeforeSubmitModalProps) => {
  const classes = useStyles();

  return (
    <Modal
      paperStyles={{ width: "80%", maxWidth: "600px" }}
      open={props.open}
      handleClose={props.handleClose}
    >
      <div className={classes.container}>
        <Typography className={classes.paragraph} variant={"h3"}>
          Sorry 😅
        </Typography>
        <Typography className={classes.paragraph} variant={"h6"}>
          You have to be logged in to submit a breakdown.
        </Typography>
        <Typography className={classes.paragraph} variant={"h6"}>
          This lets you keep track of the breakdowns you've submitted.
        </Typography>
        <Typography className={classes.paragraph} variant={"h6"}>
          This also helps me moderate the quality of the breakdowns.
        </Typography>
        <Typography
          className={classes.paragraph}
          variant={"h6"}
          align={"right"}
          style={{ marginRight: "30%" }}
        >
          - Eric
        </Typography>
      </div>
      <Button
        size={"large"}
        color={"primary"}
        variant={"contained"}
        onClick={signInWithCognito}
        className={classes.signInButton}
      >
        Sign Up / Sign In
      </Button>
    </Modal>
  );
};
