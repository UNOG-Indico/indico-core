// This file is part of Indico.
// Copyright (C) 2002 - 2025 CERN
//
// Indico is free software; you can redistribute it and/or
// modify it under the terms of the MIT License; see the
// LICENSE file for more details.

import PropTypes from 'prop-types';
import React, {useEffect, useState} from 'react';
import {Button, Message, Modal, Icon} from 'semantic-ui-react';

import {Translate, Param} from 'indico/react/i18n';
import ReactDOM from "react-dom";

const DeleteDialog = ({
  open,
  title,
  message,
  confirmText,
  onDelete,
  onClose,
  isDeleting,
  recordName,
}) => {
  const [countdown, setCountdown] = useState(10);
  const [isButtonDisabled, setButtonDisabled] = useState(true);

  useEffect(() => {
    if (open) {
      setCountdown(10);
      setButtonDisabled(true);
      const timer = setInterval(() => {
        setCountdown(prevCountdown => {
          if (prevCountdown <= 1) {
            clearInterval(timer);
            setButtonDisabled(false);
            return 0;
          }
          return prevCountdown - 1;
        });
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [open]);

  return (
    <Modal size="small" open={open} onClose={onClose} closeIcon={!isDeleting}>
      <Modal.Header>{title}</Modal.Header>
      <Modal.Content>
        <Message negative icon>
          <Icon name="warning sign" />
          <Message.Content>
            <Message.Header>
              <Translate>This action is irreversible</Translate>
            </Message.Header>
            <Translate>{message}</Translate>
          </Message.Content>
        </Message>
        <Translate as="p">Are you sure you want to delete {recordName}?</Translate>
      </Modal.Content>
      <Modal.Actions>
        <Button onClick={onClose} disabled={isDeleting} content={Translate.string('Cancel')}/>
        {isButtonDisabled ? (
          <Button color="red" disabled>
            <Translate>
              {confirmText} (<Param name="countdown_seconds" value={countdown}/>)
            </Translate>
          </Button>
        ) : (
          <Button color="red" onClick={onDelete} disabled={isDeleting} loading={isDeleting}>
            <Translate>{confirmText}</Translate>
          </Button>
        )}
      </Modal.Actions>
    </Modal>
  );
};

DeleteDialog.propTypes = {
  open: PropTypes.bool.isRequired,
  title: PropTypes.string.isRequired,
  message: PropTypes.string.isRequired,
  confirmText: PropTypes.string.isRequired,
  onDelete: PropTypes.func.isRequired,
  onClose: PropTypes.func.isRequired,
  isDeleting: PropTypes.bool,
  recordName: PropTypes.string.isRequired,
};

DeleteDialog.defaultProps = {
  isDeleting: false,
};

export default DeleteDialog;

customElements.define(
  'ind-delete-button',
  class extends HTMLElement {
    connectedCallback() {
      ReactDOM.render(
        <DeleteDialog
          title={JSON.parse(this.getAttribute('title'))}
          isAdmin={JSON.parse(this.getAttribute('user-is-admin'))}
          message={this.getAttribute('message')}
          confirmText={this.getAttribute('confirm-text')}
          recordName={this.getAttribute('record-name')}
        />,
        this
      );
    }
  }
);
