import React  from "react";
import Button from "plaid-threads/Button";


import Box from '@mui/material/Box';
import Modal from '@mui/material/Modal';

import MuiSignin from "../MuiSignin";

// Modal // 

const style = {
  position: 'absolute' as 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  width: 400,
  bgcolor: 'background.paper',
  border: '2px solid #000',
  boxShadow: 24,
  p: 4,
};

function BasicModal() {
  const [open, setOpen] = React.useState(false);
  const handleOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);

  return (
    <div>
      <Button type="button" large onClick={handleOpen}>Sign In</Button>
      <Modal
        open={open}
        onClose={handleClose}
        aria-labelledby="modal-modal-title"
        aria-describedby="modal-modal-description"
      >
        <Box sx={style}>
          <MuiSignin setOpen={setOpen} />
        </Box>
      </Modal>
    </div>
  );
}


const Signin = () => {
  return <BasicModal />;

}


Signin.displayName = "Signin";

export default Signin;
