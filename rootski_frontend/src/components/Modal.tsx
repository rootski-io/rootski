import React from "react";
import { makeStyles, Theme, createStyles } from "@material-ui/core/styles";
import MaterialModal from "@material-ui/core/Modal";
import Backdrop from "@material-ui/core/Backdrop";
import Fade from "@material-ui/core/Fade";
import Paper from "@material-ui/core/Paper";
import { Typography } from "@material-ui/core";

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    modal: {
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
    },
    paper: {
      backgroundColor: theme.palette.background.paper,
      border: "2px solid #000",
      boxShadow: theme.shadows[5],
      padding: theme.spacing(2, 4, 3),
    },
  })
);

interface ModalProps {
  open: boolean;
  paperStyles: any;

  // a function that causes the :open: prop
  // to be false, probably by calling a setModelOpen(false)
  // type React.useState type function from the parent
  handleClose: () => void;
}

// NOTE: the React.FC makes props.children work
export const Modal: React.FC<ModalProps> = (props) => {
  const classes = useStyles();

  return (
    <div>
      <MaterialModal
        aria-labelledby="transition-modal-title"
        aria-describedby="transition-modal-description"
        className={classes.modal}
        open={props.open}
        onClose={props.handleClose}
        closeAfterTransition
        BackdropComponent={Backdrop}
        BackdropProps={{
          timeout: 500,
        }}
      >
        <Fade in={props.open}>
          <Paper elevation={3} style={props.paperStyles}>
            {props.children}
          </Paper>
        </Fade>
      </MaterialModal>
    </div>
  );
};
